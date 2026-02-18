from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = Options()
#options.add_argument('--headless=new')
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
driver.get("https://www.musictheory.net/exercises/note")
#click settings button
try:
    settings_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[3]/nav/div[3]'))
    )
    settings_button.click()
except Exception as e:
    print(f"A setting button error occurred: {e}")

#edit clefts
try:
    clefs_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div[1]/div[2]/div/div/div/div[1]/div/div'))
    )
    clefs_button.click()
except Exception as e:
    print(f"A clef button error occurred: {e}")