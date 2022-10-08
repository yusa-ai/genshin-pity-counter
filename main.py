import os
import re
import subprocess
import sys
import tempfile
import time
from urllib import parse
from urllib.parse import urlencode

import requests


OUTPUT_LOG_FILE_PATH = f"{os.environ['USERPROFILE']}/AppData/LocalLow/miHoYo/Genshin Impact/output_log.txt"
DATA_FILE_NAME = "data_2"

API_MAX_PAGE_SIZE = 20
WISH_HISTORY_URL_REGEX = r"(https://hk4e-api-os.hoyoverse.com\S+&end_id=0)"

start_time = time.time()

# Fetch game directory from output_log.txt

with open(OUTPUT_LOG_FILE_PATH) as file:
    warmup_message = next((line.split("Warmup file")[1] for line in file.readlines()
                           if line.startswith("Warmup file")), None)

game_dir = warmup_message.split("/Genshin Impact game/")[0].strip()

# Initialize paths based on game directory

data_dir = f"{game_dir}/Genshin Impact game/GenshinImpact_Data/webCaches/Cache/Cache_Data"
data_file_path = f"{data_dir}/{DATA_FILE_NAME}"
temp_file_path = f"{tempfile.gettempdir()}/{DATA_FILE_NAME}"

# Delete previous data_2 from tmp

try:
    os.remove(temp_file_path)
except OSError:
    pass

# Copy data file to %temp% using PowerShell
# A standard copy will not work on Windows while Genshin Impact is running because the file is locked

cmd = f"Copy-Item \"{data_file_path}\" -Destination \"{temp_file_path}\""
process = subprocess.Popen(["powershell.exe", cmd], shell=True, stdout=sys.stdout)
process.wait()

# Use regex to find Wish History URL

try:
    with open(temp_file_path, errors="ignore") as file:
        contents = file.read()
except FileNotFoundError:
    print(f"Could not copy file to {temp_file_path}.")
    sys.exit(1)

# Iterate over matching URLs until finding one with valid data

urls = re.findall(WISH_HISTORY_URL_REGEX, contents)
for url in urls:
    response = requests.get(url)
    response.raise_for_status()
    if (response.json()["data"] is not None):
        wish_history_url = url
        break

domain = wish_history_url.split("?")[0]

# Rebuild URL GET parameters for first page

params = dict(parse.parse_qs(parse.urlsplit(wish_history_url).query))
params["page"] = 1
params["size"] = API_MAX_PAGE_SIZE
params.pop("end_id", None)

wish_history_url = f"{domain}?{urlencode(params, doseq=True)}"

response = requests.get(wish_history_url)
response.raise_for_status()


def process_wishes(wishes: dict) -> dict:
    """
    Counts wishes across page until 5-Star is found
    :param wishes: The dictionary containing said wishes
    :return: Number of wishes until 5-Star if any, if a 5-Star was found and its name, last wish id
    """
    five_s_found = False
    five_s_name = None
    count = 0

    for wish in wishes:
        if wish["rank_type"] == "5":
            five_s_found = True
            five_s_name = wish["name"]
            break

        count += 1

    return {
        "count": count,
        "five_star_found": five_s_found,
        "five_star_name": five_s_name,
        "end_id": wishes[-1]["id"]
    }


five_star_pity: int = 0
five_star_found: bool = False
five_star_name = None

four_star_pity: int = 0
four_star_found: bool = False
four_star_name = None

current_page = response.json()["data"]["list"]

# 4-Star pity

for w in current_page:
    if w["rank_type"] == "4":
        four_star_found = True
        four_star_name = w["name"]
        break
    four_star_pity += 1

# 5-Star pity

while not five_star_found:
    process_result = process_wishes(current_page)

    five_star_pity += process_result["count"]
    five_star_found = process_result["five_star_found"]
    five_star_name = process_result["five_star_name"]

    params["page"] = params["page"] + 1
    params["end_id"] = process_result["end_id"]

    wish_history_url = f"{domain}?{urlencode(params, doseq=True)}"

    response = requests.get(wish_history_url)
    response.raise_for_status()
    current_page = response.json()["data"]["list"]


if five_star_pity < 10:
    five_star_pity = f"0{five_star_pity}"

print(f"5-Star pity: {five_star_pity}/90")
if five_star_name:
    print(f"Last 5-Star wished: {five_star_name}")

print(f"4-Star pity: 0{four_star_pity}/10")
if four_star_name:
    print(f"Last 4-Star wished: {four_star_name}")


print(f"\n\nElapsed time: {round(time.time() - start_time, 2)}s")
