import os
import re
import requests
import subprocess
import sys
import tempfile
from urllib import parse
from urllib.parse import urlencode

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

first_20_items = requests.get(wish_history_url)
first_20_items.raise_for_status()

for item in first_20_items.json()["data"]["list"]:
    print(item)
