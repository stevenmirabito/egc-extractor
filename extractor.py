import csv
import email
import os
import re
from datetime import datetime
from imaplib import IMAP4, IMAP4_SSL

from bs4 import BeautifulSoup
from selenium import webdriver

import config

BRAND_REGEX = re.compile(r"Your (.*?) (?:\$\d+\s)?e?Gift card", re.IGNORECASE)
SPEC_CHARS_REGEX = re.compile(r"[^\w|'|\s]")
PIN_REGEX = re.compile(r"[A-Z0-9]{4,}")
AMOUNT_REGEX = re.compile(r"(\$(0|[1-9][0-9]{0,2})(,\d{3})*(\.\d{1,2})?)")


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
        return SPEC_CHARS_REGEX.sub("", BRAND_REGEX.search(text).group(1))
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
def fetch_codes(browser):
    # Get the card brand
    card_type = try_elements(
        [
            lambda: browser.find_element_by_xpath('//*[@id="main"]/p/strong'),
            lambda: browser.find_element_by_id("vgcheader"),
            lambda: browser.find_element_by_xpath("//title"),
            lambda: browser.find_element_by_tag_name("h1"),
        ],
        extract_func=extract_brand,
    )

    if card_type is None:
        raise RuntimeError("Unable to find card type on page")

    # Get the card number
    card_number = browser.find_element_by_id("cardNumber2").text
    card_number = re.sub(r"\s+", "", card_number)

    card_amount = try_elements(
        [
            lambda: browser.find_element_by_id("value"),
            lambda: browser.find_element_by_xpath('//*[@id="main"]/div[1]/div[2]/h2'),
            lambda: browser.find_element_by_id("amount"),
            lambda: browser.find_element_by_tag_name("h1"),
        ],
        extract_func=extract_amount,
    )

    if card_amount is None:
        raise RuntimeError("Unable to find card amount on page")

    card_pin = try_elements(
        [
            lambda: browser.find_element_by_id("secCode"),
            lambda: browser.find_element_by_id("securityCode"),
            lambda: browser.find_element_by_id("pinContainer"),
            lambda: browser.find_element_by_xpath(
                '//*[@id="main"]/div[2]/div[2]/p[2]/span'
            ),
            lambda: browser.find_element_by_xpath('//*[@id="main"]/div[4]/p[2]/span'),
        ],
        extract_func=extract_pin,
    )

    if card_pin is None:
        raise RuntimeError("Unable to find card PIN on page")

    return (card_type, card_amount, card_number, card_pin)


def main():
    # Connect to the server
    if config.IMAP_SSL:
        mailbox = IMAP4_SSL(host=config.IMAP_HOST, port=config.IMAP_PORT)
    else:
        mailbox = IMAP4(host=config.IMAP_HOST, port=config.IMAP_PORT)

    # Log in and select the configured folder
    mailbox.login(config.IMAP_USERNAME, config.IMAP_PASSWORD)
    mailbox.select(config.FOLDER)

    # Search for matching emails
    status, messages = mailbox.search(None, f"(FROM {config.FROM_EMAIL})")
    if status == "OK":
        # Convert the result list to an array of message IDs
        messages = messages[0].split()

        if len(messages) < 1:
            # No matching messages, stop
            print("No matching messages found, nothing to do.")
            exit()

        # Open the CSV for writing
        with open(
            "cards_" + datetime.now().strftime("%m-%d-%Y_%H%M%S") + ".csv",
            "w",
            newline="",
        ) as csv_file:
            # Start the browser and the CSV writer
            browser = webdriver.Chrome(config.CHROMEDRIVER_PATH)
            csv_writer = csv.writer(csv_file)

            # Create a directory for screenshots if it doesn't already exist
            screenshots_dir = os.path.join(os.getcwd(), "screenshots")
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)

            # For each matching email...
            for msg_id in messages:
                print(f"---> Processing message id {msg_id.decode('UTF-8')}...")

                # Fetch it from the server
                status, data = mailbox.fetch(msg_id, "(RFC822)")
                if status == "OK":
                    # Convert it to an Email object
                    msg = email.message_from_bytes(data[0][1])

                    # Get the HTML body payload
                    msg_html = msg.get_payload(decode=True)

                    # Save the email timestamp
                    datetime_received = datetime.fromtimestamp(
                        email.utils.mktime_tz(email.utils.parsedate_tz(msg.get("date")))
                    )

                    # Parse the message
                    msg_parsed = BeautifulSoup(msg_html, "html.parser")

                    # Find the "View Gift" link
                    egc_links = msg_parsed.findAll(
                        "a", href=True, text=re.compile("Click to View")
                    )
                    for egc_link in egc_links:
                        # Open the link in the browser
                        browser.get(egc_link["href"])

                        card_type, card_amount, card_number, card_pin = fetch_codes(
                            browser
                        )

                        # Save a screenshot
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
                                datetime_received,
                                browser.current_url,
                            ]
                        )

                        # Print out the details to the console
                        print(
                            f"{card_type}: {card_number} {card_pin}, "
                            f"{card_amount}, {datetime_received}"
                        )

                    if len(egc_links) < 1:
                        print(
                            "ERROR: Unable to find eGC link in message "
                            f"{msg_id.decode('UTF-8')}, skipping."
                        )
                else:
                    print(
                        "ERROR: Unable to fetch message "
                        f"{msg_id.decode('UTF-8')}, skipping."
                    )

            # Close the browser
            browser.close()
    else:
        print("FATAL ERROR: Unable to fetch list of messages from server.")
        exit(1)


if __name__ == "__main__":
    main()
