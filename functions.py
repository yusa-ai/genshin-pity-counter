# Genshin Wish Counter functions

import os

OUTPUT_LOG_PATH = f"{os.environ['USERPROFILE']}/AppData/LocalLow/miHoYo/Genshin Impact/output_log.txt"
WISH_HISTORY_URL_PREFIX = "OnGetWebViewPageFinish:"


def fetch_wish_history_url() -> str:
    """
    Fetch and return the URL of the wish history webpage that displays in Genshin Impact.
    This webpage needs to be open in-game when running this program.
    """
    try:
        with open(OUTPUT_LOG_PATH) as output_log:
            line = [line for line in output_log.readlines() if line.startswith(WISH_HISTORY_URL_PREFIX)]
            # It should only match one
            return line[0][len(WISH_HISTORY_URL_PREFIX):]

    except FileNotFoundError as e:
        print(e)
