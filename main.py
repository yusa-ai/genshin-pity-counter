import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from functions import *

WAIT_TIME_INITIAL_LOAD = 10
WAIT_TIME_BETWEEN_PAGES = 2
FIVE_STAR_STRING = "(5-Star)"
MAX_ENTRIES_PER_PAGE = 6

wish_history_url: str = fetch_wish_history_url()

# Initialize web driver to load and fetch the Wish History page

options = Options()
options.headless = True

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(options=options, service=service)

driver.get(wish_history_url)

# The webpage loads the wish history asynchronously, in JS. Wait for the frame holding the data to load before fetching
try:
    WebDriverWait(driver, WAIT_TIME_INITIAL_LOAD).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR,
                                                         "div#frame")))
    print("Wish History has loaded. Proceeding...")

except TimeoutException:
    print("Could not load Wish History. Aborting...")

    # TODO Check for this
    print("It may be that the previously fetched URL has now expired. Please open your Wish History in-game and "
          "try again.")

    driver.quit()
    exit(1)

else:
    # Select limited rate-up banner history

    driver.find_element(By.CSS_SELECTOR, ".type-select-container").click()

    select_items = driver.find_elements(By.CSS_SELECTOR, "ul.ul-list > li")
    item = next(item for item in select_items if item.get_attribute("data-id") == "301")
    item.click()

    time.sleep(WAIT_TIME_BETWEEN_PAGES)  # TODO wait for table to change

    # Now, check if there is any record at all
    try:
        driver.find_element(By.CSS_SELECTOR, "div.empty-row")
        print("Wish History is empty.")
        driver.quit()
        exit(0)

    except NoSuchElementException:
        pass

# Cycle through all the pages

five_star_found: bool = False
current_page: int = 1
last_page_number_of_wishes = int()

while not five_star_found:
    print(f"Fetching wishes from page {current_page}")

    rows = driver.find_elements(By.CSS_SELECTOR, "div.log-item-row")
    five_star_index = next((rows.index(row) for row in rows if FIVE_STAR_STRING in row.text), None)
    five_star_found = five_star_index is not None

    if five_star_found:
        # The index of the 5-Star is also the number of wishes made before it on the same page
        last_page_number_of_wishes = five_star_index
        five_star_name = rows[five_star_index].find_element(By.CSS_SELECTOR, "span.cell.name").text.\
            removesuffix(FIVE_STAR_STRING).strip()

        print(f"Found last 5✰ obtained: {five_star_name}")

    else:
        # Go to next page
        next_page_button = driver.find_element(By.CSS_SELECTOR, "span.page-item.to-next")
        next_page_button.click()

        # Wait until page number increments (+1). If it doesn't, there are no other pages to fetch
        try:
            wait = WebDriverWait(driver, WAIT_TIME_BETWEEN_PAGES)
            wait.until(lambda drv: int(drv.find_elements(By.CSS_SELECTOR, "span.page-item")[1].text) != current_page)
            current_page += 1
        except TimeoutException:
            last_page_number_of_wishes = len(driver.find_elements(By.CSS_SELECTOR, "div.log-item-row"))
            break

driver.quit()

five_star_pity = (current_page - 1) * MAX_ENTRIES_PER_PAGE + last_page_number_of_wishes
print(f"5✰ Pity: {five_star_pity}/90")
