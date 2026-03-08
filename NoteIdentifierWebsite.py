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
        print(f"A setting button error occurred: {e}")


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
            None
        else:
            print("Invalid accidental")
            search = False
    path_Name = (saveLocation+"\\" + name[0] + "_" + num)
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


# Makes a midi dictionary where the file name is a ket to the midi value
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
                return f"{n}_{octave}S"
            elif "b" in name:
                n = name[0]
                return f"{n}_{octave}b"
            else:
                return f"{name}_{octave}"

        midi_dict[format_key(sharp_name)] = midi
        # add flat equivalent if different
        if flat_name != sharp_name:
            midi_dict[format_key(flat_name)] = midi
    return midi_dict


# Saves a temporary screenshot of the current note value on screen and compares it to the already existing
# screenshots in the folder.
def checkScreenshot():
    # save temp screenshot of current canvas:
    driver.find_element(By.TAG_NAME, "canvas").screenshot("./temp.png")

    # Compare images in file
    # https://cloudinary.com/guides/image-effects/beginners-guide-to-image-comparison-in-python
    tempImage = np.array(Image.open('./temp.png'))

    # loop variables
    sameImage = False
    files = list(Path("./Screenshots").iterdir())
    fileNum = 0

    # loops until image is the same or the file index gets too large and throws an error
    while not sameImage:
        try:
            savedRefImg = np.array(Image.open(files[fileNum]))
        except:
            break
        # Check if the shapes are the same and pixels are identical
        if tempImage.shape == savedRefImg.shape and np.all(tempImage == savedRefImg):
            sameImage = True
        else:
            fileNum +=1

    # delete temp img
    if Path("./temp.png").exists():
        Path("./temp.png").unlink()
    if sameImage:
        return files[fileNum].stem
    else:
        return "The screenshot does not match any existing imgs"




# current problem: screenshots with different note values (whole vs half vs quarter, etc.)
# in the future different directories with images for each note value to compare

getScreenshots()