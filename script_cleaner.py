import pandas as pd
import re
from places import places
from characters import characters

script_path = "pulp_fiction_script.txt"

def string_conversions(data):
    data["Character (in script)"] = data["Character (in script)"].str.title()

    # Manually change cases that don't work with str.title()
    data["Character (in script)"] = data["Character (in script)"].str.replace("Woman\'S Voice", "Woman\'s voice")
    data["Character (in script)"] = data["Character (in script)"].str.replace("Young Man", "Young man")
    data["Character (in script)"] = data["Character (in script)"].str.replace("Young Woman", "Young woman")
    data["Character (in script)"] = data["Character (in script)"].str.replace("Fourth Man", "Fourth man")
    data["Character (in script)"] = data["Character (in script)"].str.replace("Looky-Loo Woman", "Looky-loo woman")

    data["Character (actual)"] = data["Character (actual)"].str.title()

    # Manually change cases that don't work with str.title()
    data["Character (actual)"] = data["Character (actual)"].str.replace("Fourth Man", "Fourth man")
    data["Character (actual)"] = data["Character (actual)"].str.replace("Looky-Loo Woman", "Looky-loo woman")

    data.Place = data.Place.str.lower()

    # Manually change cases that don't work with str.lower()
    data.Place = data.Place.str.replace("chevy", "Chevy")
    data.Place = data.Place.str.replace("sally leroy\'s", "Sally LeRoy\'s")
    data.Place = data.Place.str.replace("lance\'s", "Lance\'s")
    data.Place = data.Place.str.replace("marcellus", "Marsellus")
    data.Place = data.Place.str.replace("marsellus", "Marsellus")
    data.Place = data.Place.str.replace("wallace", "Wallace")
    data.Place = data.Place.str.replace("jackrabbit slim", "Jackrabbit Slim")
    data.Place = data.Place.str.replace("parked/raining", "parked / raining")
    data.Place = data.Place.str.replace("willis locker", "Willis locker")
    data.Place = data.Place.str.replace("honda", "Honda")
    data.Place = data.Place.str.replace("butch", "Butch")
    data.Place = data.Place.str.replace("mason-dixie pawnshop", "Mason-Dixie pawnshop")
    data.Place = data.Place.str.replace("russell", "Russell")
    data.Place = data.Place.str.replace("nova", "Nova")
    data.Place = data.Place.str.replace("jimmie", "Jimmie")
    data.Place = data.Place.str.replace("monster joe\'s truck and tow", "Monster Joe\'s Truck and Tow")
    data.Place = data.Place.str.replace("vincent", "Vincent")
    
    data.Time = data.Time.str.lower()


def special_cases(data):
    # There's a scene where picture cuts back and forth, and the location isn't specified in the script so it goes unnoticed by the algorithm.
    # Manually change the locations to the right locations
    data.loc[(data['Place'] == "VINCENT IN THE MALIBU") & (data['Character (in script)'] == "VINCENT"), ['Place', 'Time']] = ["INT. VINCENT'S MALIBU (MOVING)", "NIGHT"]
    data.loc[(data['Place'] == "VINCENT IN THE MALIBU") & ((data['Character (in script)'] == "LANCE") | (data['Character (in script)'] == "JODY")), ['Place', 'Time']] = ["INT. LANCE'S HOUSE", "NIGHT"]


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


def count_words(speaking_turn):
    splits = speaking_turn.split()
    count = len(splits)
    for word in splits:
        if word == "–" or word == '-':
            count = count - 1

    return count

def actual_character(character):
    if character == "YOUNG WOMAN" or character == "YOLANDA":
        return "HONEY BUNNY"
    if character == "YOUNG MAN" or character == "PATRON":
        return "PUMPKIN"
    if character == "WINSTON":
        return "THE WOLF"
    if character == "WOMAN'S VOICE":
        return "MOTHER"
    return character


def script_data():
    data_rows = []
    character = None
    place = None
    time = None
    speaking_turn = ""
    off_screen = False
    voice_over = False

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

                # (V.O.) means voice over.
                # remove marking to not interpret it as new character
                if " (V.O.)" in line:
                    voice_over = True
                    line = line.replace(" (V.O.)", "")
                
                if line in characters:
                    character = line
                
                continue

            # If empty line, character is not speaking anymore
            if not line:
                
                # Add line to a character
                if character is not None:
                    speaking_turn = remove_parenthesis(speaking_turn)
                    word_count = count_words(speaking_turn)
                    data_rows.append({"Character (in script)": character, "Character (actual)": actual_character(character), "Off screen": off_screen, "Voice-over": voice_over, "Place": place, "Time": time, "Line": speaking_turn, "Word count": word_count})
                
                character = None
                speaking_turn = ""
                off_screen = False
                voice_over = False
                continue

            # If we got this far, a speaking turn is not over.
            # Concatenate this line to the ongoing speaking turn
            speaking_turn = " ".join([speaking_turn, line])
    
    data = pd.DataFrame(data_rows)
    special_cases(data)
    string_conversions(data)

    data["Line number"] = pd.Series([ x for x in range(1, len(data)+1) ])
    data = data.set_index("Line number", drop=True)

    # Some places don't get recorded: forward filling NaN values sets the location to be previous location if not specified in the script
    # This is valid place for all cases
    data = data.fillna(method='ffill')

    return data
    

data = script_data()
print(data.to_csv())