import argparse
import csv
import os
import re
from datetime import datetime

from bs4 import BeautifulSoup
from imap_tools import AND, MailBox
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config

VIEW_LINK_REGEX = re.compile(r".*View (?!this email).*", re.IGNORECASE)
BRAND_REGEX = re.compile(
    r"(Your )?(.*?) (?:\$\d+\s)?(e?Gift|Bonus) card", re.IGNORECASE
)
SPEC_CHARS_REGEX = re.compile(r"[^\w|'|\s]")
PIN_REGEX = re.compile(r"[A-Z0-9]{4,}")
AMOUNT_REGEX = re.compile(r"(\$(0|[1-9][0-9]{0,2})(,\d{3})*(\.\d{1,2})?)")

service = Service(config.CHROMEDRIVER_PATH)


class WebdriverBrowser:
    def __enter__(self):
        self.browser = webdriver.Chrome(service=service)
        return self.browser

    def __exit__(self, *args, **kwargs):
        self.browser.close()


def try_elements(getters, extract_func=None):
    results = []

    for getter in getters:
        try:
            result = getter().get_attribute("innerText")

            if extract_func:
                result = extract_func(result)

            results.append(result)
        except Exception:  # nosec
            pass

    results = [r for r in results if r is not None and r != ""]

    if len(results) < 1:
        return None

    return results[0].strip()


def extract_brand(text):
    try:
        return SPEC_CHARS_REGEX.sub("", BRAND_REGEX.search(text).group(2))
    except Exception:
        return None


def extract_number(text):
    try:
        return re.sub(r"\s+", "", text)
    except Exception:
        return None


def extract_amount(text):
    try:
        return AMOUNT_REGEX.search(text).group(1)
    except Exception:
        return None


def extract_pin(text):
    try:
        return PIN_REGEX.search(text)[0]
    except Exception:
        return None


# Fetch codes from DOM
def fetch_codes(browser, has_pin=True):
    # Get the card brand
    card_type = try_elements(
        [
            lambda: browser.find_element(By.XPATH, '//*[@id="main"]/p/strong'),
            lambda: browser.find_element(By.ID, "vgcheader"),
            lambda: browser.find_element(By.XPATH, "//title"),
            lambda: browser.find_element(By.CLASS_NAME, "section-header"),
            lambda: browser.find_element(By.TAG_NAME, "h1"),
        ],
        extract_func=extract_brand,
    )

    if card_type is None:
        raise RuntimeError("Unable to find card type on page")

    # Get the card number
    card_number = try_elements(
        [
            lambda: browser.find_element(By.ID, "cardNumber2"),
            lambda: browser.find_element(By.ID, "accountnumber"),
            lambda: browser.find_element(
                By.CSS_SELECTOR,
                (
                    "div[aria-label$='Card Number'] "
                    ".utility-button-secondary-text-style"
                ),
            ),
        ],
        extract_func=extract_number,
    )

    if card_number is None:
        raise RuntimeError("Unable to find card number on page")

    card_amount = try_elements(
        [
            lambda: browser.find_element(By.ID, "value"),
            lambda: browser.find_element(By.ID, "amount"),
            lambda: browser.find_element(By.ID, "balance-amount"),
            lambda: browser.find_element(By.ID, "giftvalue"),
            lambda: browser.find_element(By.XPATH, '//*[@id="main"]/div[1]/div[2]/h2'),
            lambda: browser.find_element(By.TAG_NAME, "h1"),
        ],
        extract_func=extract_amount,
    )

    if card_amount is None:
        raise RuntimeError("Unable to find card amount on page")

    card_pin = try_elements(
        [
            lambda: browser.find_element(By.ID, "secCode"),
            lambda: browser.find_element(By.ID, "securityCode"),
            lambda: browser.find_element(By.ID, "pinContainer"),
            lambda: browser.find_element(
                By.CSS_SELECTOR,
                ("div[aria-label='Copy PIN'] " ".utility-button-secondary-text-style"),
            ),
            lambda: browser.find_element(
                By.XPATH, '//*[@id="main"]/div[2]/div[2]/p[2]/span'
            ),
            lambda: browser.find_element(By.XPATH, '//*[@id="main"]/div[4]/p[2]/span'),
        ],
        extract_func=extract_pin,
    )

    if has_pin and card_pin is None:
        raise RuntimeError("Unable to find card PIN on page")

    return (card_type, card_amount, card_number, card_pin)


def process_messages(browser, csv_writer, messages, has_pin=True, screenshots_dir=None):
    for msg in messages:
        print(f"---> Processing message id {msg.uid}...")

        # Parse the message
        msg_parsed = BeautifulSoup(msg.html, "html.parser")

        # Find the "View Gift" link
        egc_links = msg_parsed.find_all("a", href=True, text=VIEW_LINK_REGEX)

        if len(egc_links) < 1:
            # Check for image link (wgiftcard)
            activate_img = msg_parsed.find("img", alt=re.compile(r"activate.*"))

            if activate_img:
                egc_link = activate_img.find_parent("a")
                if egc_link:
                    egc_links = [egc_link]

        if len(egc_links) < 1:
            print("ERROR: Unable to find eGC link in message " f"{msg.uid}, skipping.")
            continue

        for egc_link in egc_links:
            # Open the link in the browser
            browser.get(egc_link["href"])

            # Handle security page
            try:
                email_field = browser.find_element(By.ID, "challenge-email")
                email_field.send_keys(msg.to)
                submit_btn = browser.find_element(
                    By.CSS_SELECTOR, "button[type='submit']"
                )
                submit_btn.click()
            except NoSuchElementException:
                pass

            # Skip the envelope
            try:
                skip_btn = browser.find_element(By.ID, "skip")
                WebDriverWait(browser, 10).until(EC.element_to_be_clickable(skip_btn))
                skip_btn.click()
            except NoSuchElementException:
                pass

            card_type, card_amount, card_number, card_pin = fetch_codes(
                browser, has_pin=has_pin
            )

            # Save a screenshot
            if screenshots_dir:
                browser.save_screenshot(
                    os.path.join(screenshots_dir, card_number + ".png")
                )

            # Write the details to the CSV
            csv_writer.writerow(
                [
                    card_type,
                    card_number,
                    card_pin,
                    card_amount,
                    msg.date,
                    browser.current_url,
                ]
            )

            # Print out the details to the console
            print(
                f"{card_type}: {card_number} {card_pin}, " f"{card_amount}, {msg.date}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Extract gift cards from delivery emails"
    )

    parser.add_argument(
        "--no-pin",
        dest="pin",
        action="store_false",
        help="Specify if the gift cards do not have PINs",
    )

    args = parser.parse_args()

    # Connect to the server
    with MailBox(config.IMAP_HOST, port=config.IMAP_PORT).login(
        config.IMAP_USERNAME, config.IMAP_PASSWORD, initial_folder=config.FOLDER
    ) as mailbox:
        messages = mailbox.fetch(AND(from_=config.FROM_EMAIL))

        # Start the browser
        with WebdriverBrowser() as browser:
            # Open the CSV for writing
            with open(
                "cards_" + datetime.now().strftime("%m-%d-%Y_%H%M%S") + ".csv",
                "w",
                newline="",
            ) as csv_file:
                # Start the CSV writer
                csv_writer = csv.writer(csv_file)

                # Create a directory for screenshots if it doesn't already exist
                if config.SCREENSHOTS:
                    screenshots_dir = os.path.join(os.getcwd(), "screenshots")
                    if not os.path.exists(screenshots_dir):
                        os.makedirs(screenshots_dir)

                    process_messages(
                        browser,
                        csv_writer,
                        messages,
                        has_pin=args.pin,
                        screenshots_dir=screenshots_dir,
                    )
                else:
                    process_messages(browser, csv_writer, messages, has_pin=args.pin)


if __name__ == "__main__":
    main()
