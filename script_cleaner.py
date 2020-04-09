import pandas as pd
import re
from places import places
from characters import characters

script_path = "pulp_fiction_script.txt"

def string_conversions(data):
    data.Character = data.Character.str.title()
    data.Place = data.Place.str.title()
    data.Time = data.Time.str.lower()

def special_cases(data):
    # There's a scene where picture cuts back and forth, and the location isn't specified in the script so it goes unnoticed by the algorithm.
    # Manually change the locations to the right locations
    data.loc[(data['Place'] == "VINCENT IN THE MALIBU") & (data['Character'] == "VINCENT"), ['Place', 'Time']] = ["INT. VINCENT'S MALIBU (MOVING)", "NIGHT"]
    data.loc[(data['Place'] == "VINCENT IN THE MALIBU") & ((data['Character'] == "LANCE") | (data['Character'] == "JODY")), ['Place', 'Time']] = ["INT. LANCE'S HOUSE", "NIGHT"]


def remove_parenthesis(speaking_turn):
    speaking_turn = re.sub(r'\((.*?)\)', '', speaking_turn)
    speaking_turn = re.sub(r'\s\s', ' ', speaking_turn)
    return speaking_turn.strip()

def place_and_time(line):
    splits = line.rsplit("–", maxsplit=1)
    place = splits[0].strip()
    if len(splits) == 2:
        time = splits[1].strip()
    else:
        time = None

    return (place, time)


def script_data():
    data_rows = []
    character = None
    place = None
    time = None
    speaking_turn = ""
    off_screen = False

    with open(script_path) as script:
        for line in script:
            
            # Remove newline
            line = line[:-1]

            # Check who is speaking
            if line.isupper():

                if line in places:
                    place,time = place_and_time(line)
                
                # (O.S.) means the character speaks offscreen,
                # remove marking to not interpret it as new character
                if " (O.S.)" in line:
                    off_screen = True
                    line = line.replace(" (O.S.)", "")
                
                if line in characters:
                    character = line
                
                continue

            # If empty line, character is not speaking anymore
            if not line:
                
                # Add line to a character
                if character is not None:
                    speaking_turn = remove_parenthesis(speaking_turn)
                    word_count = len(speaking_turn.split())
                    data_rows.append({"Character": character, "Off screen": off_screen, "Place": place, "Time": time, "Line": speaking_turn, "Word count": word_count})
                
                character = None
                speaking_turn = ""
                off_screen = False
                continue

            # If we got this far, a speaking turn is not over.
            # Concatenate this line to the ongoing speaking turn
            speaking_turn = " ".join([speaking_turn, line])
    
    data = pd.DataFrame(data_rows)
    special_cases(data)
    string_conversions(data)

    data["Line number"] = pd.Series([ x for x in range(1, len(data)+1) ])
    data = data.set_index("Line number", drop=True)

    return data

data = script_data()
print(data.to_string())


#TODO: some characters are in fact the same character, at least young woman, Wolanda and honey bunny, as well as pumpkin and young man.
# Also Winston is The Wolf
# Also WOMAN'S VOICE is MOTHER
#TODO: there's a line by both LANCE AND VINCENT