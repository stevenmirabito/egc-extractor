# Universal eGift Card Extractor

This script will attempt to extract the card type, amount, number, and PIN
given the claim emails sent by Staples.com and write it to a CSV. The script
will also take a screenshot of each card and save it to `screenshots` in the
current working directory.

## Installation

Download or clone this repo and install [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/).
Copy `config.sample.py` to `config.py` and update the configuration as needed,
ensuring that `CHROMEDRIVER_PATH` is a fully-qualified path to the ChromeDriver
binary. Install the dependencies with `pip install -r requirements.txt`. 

## Caveats

Different eGCs may have slightly different page layouts, which might break
this script. To modify the script for a card with a different layout, inspect
the element and copy its XPath, then replace the appropriate XPath in the
script with the one from the page.
