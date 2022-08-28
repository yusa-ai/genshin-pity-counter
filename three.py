import os
import re
from typing import Dict, Any

import requests
import subprocess
import sys
import tempfile
import time
from urllib import parse
from urllib.parse import urlencode

start_time = time.time()

OUTPUT_LOG_FILE_PATH = f"{os.environ['USERPROFILE']}/AppData/LocalLow/miHoYo/Genshin Impact/output_log.txt"
DATA_FILE_NAME = "data_2"

# Fetch game directory from output_log.txt

with open(OUTPUT_LOG_FILE_PATH) as file:
    warmup_message = next((line.split("Warmup file")[1] for line in file.readlines()
                           if line.startswith("Warmup file")), None)

game_dir = warmup_message.split("/Genshin Impact game/")[0].strip()

# Initialize paths based on game directory

data_dir = f"{game_dir}/Genshin Impact game/GenshinImpact_Data/webCaches/Cache/Cache_Data"
data_file_path = f"{data_dir}/{DATA_FILE_NAME}"
temp_file_path = f"{tempfile.gettempdir()}/{DATA_FILE_NAME}"

# Copy data file to %temp% using PowerShell
# A standard copy will not work on Windows while Genshin Impact is running because the file is locked

cmd = f"Copy-Item \"{data_file_path}\" -Destination \"{temp_file_path}\""
subprocess.Popen(["powershell.exe", cmd], shell=True, stdout=sys.stdout)

# Use regex to find Wish History URL

with open(temp_file_path, errors="ignore") as file:
    contents = file.read()

wish_history_url = re.findall(r"(https://hk4e-api-os.hoyoverse.com\S+&end_id=0)", contents)[-1]
domain = wish_history_url.split("?")[0]

# Rebuild URL GET parameters for first page

params = dict(parse.parse_qs(parse.urlsplit(wish_history_url).query))
params["page"] = 1
params["size"] = 20
params.pop("end_id", None)

wish_history_url = f"{domain}?{urlencode(params, doseq=True)}"

response = requests.get(wish_history_url)
response.raise_for_status()


def process_wishes(wishes: dict) -> dict[int | bool | str | str]:
    """
    Count wishes until five star if any is found
    :param wishes: The dictionary of wishes returned by the API
    :return: The number of wishes counted, if the five star was found or not and the id of the last wish
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
five_star_name: str = ""

current_page = response.json()["data"]["list"]

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


print(f"5-Star pity: {five_star_pity}")
if five_star_name:
    print(f"Last 5-Star wished: {five_star_name}")


print(f"\n\nElapsed time: {round(time.time() - start_time, 2)}s")
