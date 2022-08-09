import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from functions import *

WAIT_TIME_INITIAL_LOAD = 10
WAIT_TIME_BETWEEN_PAGES = 3
FIVE_STAR_STRING = "(5-Star)"

wish_history_url: str = fetch_wish_history_url()

# Initialize web driver to load and fetch the Wish History page

options = Options()
options.headless = True

service = Service("./geckodriver-v0.31.0-win64/geckodriver.exe")

driver = webdriver.Firefox(options=options, service=service)

driver.get(wish_history_url)

# The webpage loads the wish history asynchronously, in JS. Wait 10s for a table row (1 wish) to load, then
# fetch all the table rows in view
try:
    WebDriverWait(driver, WAIT_TIME_INITIAL_LOAD).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR,
                                                         "div.table-content")))
    print("Wish History has loaded. Proceeding...")
except TimeoutException:
    print("Loading is taking too much time. Aborting...")

    # Wish History URLs expire after a certain time
    if os.path.exists(LOCAL_URL_PATH):
        os.remove(LOCAL_URL_PATH)
        print("It may be that the previously fetched URL has now expired. Please open your Wish History in-game and "
              "try again.")

    exit(1)

else:
    # Now, check if there is any record at all
    try:
        driver.find_element(By.CSS_SELECTOR, "div.empty-row")
        print("Wish History is empty.")
        exit(0)

    except NoSuchElementException:
        pass

# Cycle through all the pages

five_star_found: bool = False
page_count: int = 1
table_rows: str = str()

while not five_star_found:
    print(f"Fetching wishes from page {page_count}")
    time.sleep(WAIT_TIME_BETWEEN_PAGES)

    first_row = driver.find_element(By.CLASS_NAME, "log-item-row")
    parent_div = first_row.find_element(By.XPATH, "..")

    rows = parent_div.get_attribute("innerHTML")
    table_rows += rows

    if FIVE_STAR_STRING in rows:
        five_star_found = True
        print("Found 5-Star. Fetching done.")
    else:
        # Go to next page
        next_page_button = driver.find_element(By.CSS_SELECTOR, "span.page-item.to-next")
        next_page_button.click()
        page_count += 1

        # TODO Handle case where no 5-star is found by checking page number

driver.quit()

soup = BeautifulSoup(table_rows, "html.parser")
# print(soup.prettify())
