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
            lines = output_log.readlines()

            for line in lines:
                if line.startswith(WISH_HISTORY_URL_PREFIX):
                    return line[len(WISH_HISTORY_URL_PREFIX):]

    except FileNotFoundError as e:
        print(e)
