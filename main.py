from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from functions import *

wish_history_url = fetch_wish_history_url()

# Initialize web driver to load and fetch the Wish History page

options = Options()
options.headless = True

service = Service("./geckodriver-v0.31.0-win64/geckodriver.exe")

driver = webdriver.Firefox(options=options, service=service)

driver.get(wish_history_url)

# The webpage loads the wish history asynchronously, in JS. Wait 10s for a table row (1 wish) to load, then
# fetch all the table rows in view

try:
    row = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR,
                                                                                           "span.cell.name.item_3")))
    print("History has loaded. Proceeding...")
except TimeoutException:
    print("Loading took too much time. Aborting...")

first_row = driver.find_element(By.CLASS_NAME, "log-item-row")
parent_div = first_row.find_element(By.XPATH, "..")

table_rows = parent_div.get_attribute("innerHTML")

soup = BeautifulSoup(table_rows, "html.parser")
print(soup.prettify())
