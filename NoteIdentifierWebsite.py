from pathlib import Path
from PIL import Image
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Options for driver (headless = do not show window) (detach = keep window open after program ends)
options = Options()
# options.add_argument('--headless=new')
# options.add_experimental_option("detach", True)

# save browsing data so the user only has to select options once (way easier than coding the setting clicking manually)
options.add_argument(r"user-data-dir=C:\Users\V\selenium_profile")

# initialize driver and open link
driver = webdriver.Chrome(options=options)
driver.get("https://www.musictheory.net/exercises/note")


# checks if the note input is in the format noteAccidental (eg. C#) not (#C) maybe fix this later
# returns a tuple of the form (input, Boolean for a good input)
def filterInputNote(inputNote):
    noteList = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
    inputNote = "".join(inputNote.split()).capitalize()
    if len(inputNote) > 2 or len(inputNote) < 1:
        print("The input should be 2 or 1 characters long")
        return inputNote, False
    if inputNote[0] not in noteList:
        print("This is not an existing note")
        return inputNote, False
    if len(inputNote) > 1:
        if not (inputNote[1] == "#" or inputNote[1] == "b"):
            print("This accidental is not accepted")
            return inputNote + " ", False
    return inputNote, True


# finds the correct x-path to one of the note buttons on the webpage
# note is a one-character letter corresponding to a musical note
# accidental is  a '#' or 'b' representing a sharp or a flat
def click_note(note, accidental=None):
    if accidental is None:
        xpath = f"""
        //div[@role='button'
        and .//span[contains(text(),'{note}')]
        and not(.//span[contains(@class,'use-theory-font')])]
        """
    else:
        xpath = f"""
        //div[@role='button'
        and .//span[contains(text(),'{note}')]
        and .//span[contains(@class,'use-theory-font') and contains(text(),'{accidental}')]]
        """
    try:
        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
    except Exception as e:
        print(f"A button click error occured: {e}")


# Save screenshot file to "Screenshots" directory
# Only used once to gather initial screenshots
# Manual naming to identify notes
# name is the note that was inputted earlier
def save_file(name, saveLocation):
    num = input("Write a number for note value or type x to stop: ")
    search = True
    if len(name) > 1:
        if name[1] == '#':
            name[1] = "S"
        elif name[1] == "b":
            pass
        else:
            print("Invalid accidental")
            search = False
    path_Name = (saveLocation + "\\" + name + "_" + num)
    file_path = Path(path_Name + '.png')
    while search and num != "x":
        if file_path.exists():
            print("That screenshot already exists.")
            search = False
        else:
            canvas = driver.find_element(By.TAG_NAME, "canvas")
            canvas.screenshot(path_Name + ".png")
            search = False


# Loop to run through program to manually save screenshots
def getScreenshots():
    note_type = input("What type of note will be saved?\n(ex.whole, half ,quarter: ")
    if not Path("./Screenshots_" + note_type).exists():
        Path("Screenshots_" + note_type).mkdir()
    savelocation = "./Screenshots_" + note_type
    note_input = None
    while note_input != 'x':
        note_input = input("Note: ")
        filtered = filterInputNote(note_input)
        while not filtered[1]:
            note_input = input("That was an incorrect note: ")
            filtered = filterInputNote(note_input)

        else:
            save_file(note_input, savelocation)

            # If note is not an accidental then filtered[0][1] does not exist and throws an error
            try:
                click_note(filtered[0][0], filtered[0][1])
            except:
                click_note(filtered[0][0])
        numFiles(savelocation)


# Counts the files in a directory (for max range on grand staff should be 37 with no accidentals, 85 with accidentals)
def numFiles(directoryName):
    search_path = Path('./' + directoryName)
    n_files = len([p for p in search_path.iterdir() if p.is_file()])
    print(f'Number of files: {n_files}')


# adds 1 to the screenshots names to fix the original naming mistake
def fixScreenshotNames():
    folder = Path("./Screenshots")
    files = sorted(folder.iterdir(), reverse=True)
    for file in files:
        if file.is_file():
            parts = file.stem.split("_")
            if parts[-1].isdigit():
                number = int(parts[-1]) + 1
                prefix = "_".join(parts[:-1])
                new_name = f"{prefix}_{number}{file.suffix}"
                file.rename(file.with_name(new_name))


# Returns a midi dictionary where the file name is a ket to the midi value
# Generated with chatgpt
def generateMidiDict():
    notes_sharp = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    notes_flat = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    midi_dict = {}

    for midi in range(33, 93):  # A1 (33) to G#6 (92)
        octave = (midi // 12) - 1
        i = midi % 12
        sharp_name = notes_sharp[i]
        flat_name = notes_flat[i]

        def format_key(name):
            if "#" in name:
                n = name[0]
                return f"{n}S_{octave}"
            elif "b" in name:
                n = name[0]
                return f"{n}b_{octave}"
            else:
                return f"{name}_{octave}"

        sharp_key = format_key(sharp_name)
        flat_key = format_key(flat_name)

        if midi not in midi_dict:
            midi_dict[midi] = []

        midi_dict[midi].append(sharp_key)

        if flat_name != sharp_name:
            midi_dict[midi].append(flat_key)

    return midi_dict


# Saves a temporary screenshot of the current note value on screen and compares it to the already existing
# screenshots in the folder.
def checkScreenshot(noteName):
    # save temp screenshot of current canvas:
    driver.find_element(By.TAG_NAME, "canvas").screenshot("./temp.png")

    # Compare images in file
    # https://cloudinary.com/guides/image-effects/beginners-guide-to-image-comparison-in-python
    tempImage = np.array(Image.open('./temp.png'))

    # loop variables
    sameImage = False
    print(noteName)
    folders = [p for p in Path("./").glob("Screenshots*") if p.is_dir()]
    print(folders)
    for folder in folders:
        files = list(folder.iterdir())
        for file in files:
            print(noteName in str(file))
            if noteName not in str(file):
                continue
            try:
                savedRefImg = np.array(Image.open(file))
            except:
                break

            # Check if the shapes are the same and pixels are identical
            print(tempImage.shape, savedRefImg.shape)
            print(np.all(tempImage == savedRefImg))
            if tempImage.shape == savedRefImg.shape and np.all(tempImage == savedRefImg):
                sameImage = True
                break
        if sameImage:
            return file.stem.replace("S", "#")

    # delete temp img
    if Path("./temp.png").exists():
        Path("./temp.png").unlink()
    return False


# runs the actual "game" while taking inputs from the pianoInput function
def run():
    midi_dict = generateMidiDict()
    print(midi_dict)
    while True:
        midi_value = pianoInput()
        if midi_value == 21:
            break
        correctOctave = True
        noteNames = midi_dict[midi_value]
        result = False
        for noteName in noteNames:
            note_value = noteName.split('_')
            result = checkScreenshot(note_value[0])
            print(note_value, result)
            if result:
                if note_value[0] == result.split('_')[0] and note_value[1] != result.split('_')[1]:
                    print("You clicked the right note, but in the wrong octave. Please try a different octave!")
                    correctOctave = False
                    break
        if correctOctave:
            try:
                click_note(note_value[0][0], note_value[0][1])
            except:
                click_note(note_value[0][0])

        # check if note value is correct but not right octave


# takes an input from the keyboard and returns its midi value as an int
def pianoInput():
    return int(input("Midi_Value: "))


run()
