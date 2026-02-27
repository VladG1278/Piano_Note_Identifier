from pathlib import Path
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
def filterInputNote(input):
    noteList = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
    input = "".join(input.split()).capitalize()
    if len(input) > 2 or len(input) < 1:
        print("The input should be 2 or 1 characters long")
        return input, False
    if input[0] not in noteList:
        print("This is not an existing note")
        return input, False
    if len(input) > 1:
        if not (input[1] == "#" or input[1] == "b"):
            print("This accidental is not accepted")
            return input + " ", False
    return input, True


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

    element = driver.find_element(By.XPATH, xpath)
    element.click()


# Save screenshot file to "Screenshots" directory
# Only used once to gather initial screenshots
# Manual naming to identify notes
# name is the note that was inputted earlier
def save_file(name):
    num = input("Write a number for note value or type x to stop: ")
    search = True
    path_Name = (name + "_" + num)
    file_path = Path(path_Name)
    while search and num != "x":
        if file_path.is_file():
            num = input("That screenshot already exists.")
            search = False
        else:
            canvas = driver.find_element(By.TAG_NAME, "canvas")
            canvas.screenshot("Screenshots/" + path_Name + ".png")
            search = False


# Loop to run through program to manually save screenshots
def getScreenshots ():
    note_input = None
    while note_input !='x':
        note_input = input("Note: ")
        filtered = filterInputNote(note_input)
        if not filtered[1]:
            note_input = input("That was an incorrect note: ")
            #driver.close()
        else:
            save_file(note_input)
            print(filtered)

            # If note is not an accidental then filtered[0][1] does not exist and throws an error
            try:
                click_note(filtered[0][0], filtered[0][1])
            except:
                click_note(filtered[0][0])


getScreenshots()