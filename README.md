
# Genshin Pity Counter

A very small Python script that acts as a pity counter for Genshin Impact.  
Made for convenience and to learn about web scraping ([pre-3.0 branch](https://github.com/yusa-ai/genshin-pity-counter/tree/pre-3.0)).


## Technicals

This script does 2 things:
- Get the Wish History URL of your Genshin Impact account. The Wish History page launched from the game is a web page displayed in a standard web browser.
- Fetch the wishes from the page using Genshin Impact's API, counting them and then printing the current pity progress for both 4 and 5 stars to the console.

For both pre-3.0 (now useless) and 3.0 versions of the game, this script uses the techniques used by [Paimon.moe](https://paimon.moe/) and described [here](https://gist.github.com/MadeBaruna/1d75c1d37d19eca71591ec8a31178235) to get the Wish History URL from the game files.
## Requirements

- Python 3.10.X
- pip (should be included with a standard Python install)
- PowerShell
## Installation

Either download the project's source code or clone this repository, then install its dependencies using `pip`

```bash
pip install -r requirements.txt
```
    
## Usage

_After opening the Wish History page once during your game session, and while Genshin Impact is still open,_ run:

```bash
python main.py
```

### Example output

```bash
5-Star pity: 00/90
Last 5-Star wished: Sangonomiya Kokomi
4-Star pity: 03/10
Last 4-Star wished: Xingqiu
```


## Acknowledgements

 - [Paimon.moe](https://paimon.moe/) [(repo)](https://github.com/MadeBaruna/paimon-moe)

## License

[MIT](https://raw.githubusercontent.com/yusa-ai/genshin-pity-counter/main/LICENSE)

