# Genshin Wish Counter functions

import os

LOCAL_URL_PATH = "url.txt"
OUTPUT_LOG_PATH = f"{os.environ['USERPROFILE']}/AppData/LocalLow/miHoYo/Genshin Impact/output_log.txt"
OUTPUT_LOG_URL_PREFIX = "OnGetWebViewPageFinish:"
WISH_HISTORY_URL_PREFIX = "https://webstatic-sea.hoyoverse.com/genshin/event/e20190909gacha/index.html"


def fetch_wish_history_url() -> str:
    """
    Fetch and return the URL of the wish history webpage that displays in Genshin Impact.
    This webpage needs to be open in-game when running this program.
    """

    # Try to fetch the URL locally first

    try:
        with open(LOCAL_URL_PATH) as file:
            print("Local URL found.")
            return file.readline()

    except FileNotFoundError:
        print("No local URL found. Fetching it from the game...")

        # Fetch it from the game's output log

        try:
            with open(OUTPUT_LOG_PATH) as output_log:
                prefix_matches = [line[len(OUTPUT_LOG_URL_PREFIX):] for line in output_log.readlines() if
                                  line.startswith(OUTPUT_LOG_URL_PREFIX)]

                if len(prefix_matches) == 0:
                    raise FileNotFoundError

                # It should only match exactly one
                wish_history_matches = [url for url in prefix_matches if url.startswith(WISH_HISTORY_URL_PREFIX)]

                if len(wish_history_matches) == 0:
                    raise FileNotFoundError

                url = wish_history_matches[0]

                # Save it locally to speed up next run
                with open(LOCAL_URL_PATH, "w") as file:
                    file.write(url)

                return url

        except FileNotFoundError:
            print("Wish History URL not found. Make sure Wish History is open in-game before running this program.")
            exit(1)
