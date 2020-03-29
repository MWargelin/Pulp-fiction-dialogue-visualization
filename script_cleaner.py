import pandas as pd
from places import places
from characters import characters

script_path = "pulp_fiction_script.txt"

def script_data():
    data_rows = []
    character = None
    place = None
    speaking_turn = ""
    off_screen = False

    with open(script_path) as script:
        for line in script:
            
            # Remove newline
            line = line[:-1]

            # Check who is speaking
            if line.isupper():

                if line in places:
                    place = line
                
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
                    word_count = len(speaking_turn.split())
                    data_rows.append({"Character": character, "Off screen": off_screen, "Place": place, "Line": speaking_turn, "Word count": word_count})
                
                character = None
                speaking_turn = ""
                off_screen = False
                continue

            # If we got this far, a speaking turn is not over.
            # Concatenate this line to the ongoing speaking turn
            speaking_turn = " ".join([speaking_turn, line])
        
    return pd.DataFrame(data_rows)


print(script_data().to_string())

#TODO: some characters are in fact the same character, at least young woman, Wolanda and honey bunny, as well as pumpkin and young man. Also Winston is The Wolf
#TODO: there's a line by both LANCE AND VINCENT
#TODO: Remove words in brackets?
#TODO: Offscreen

