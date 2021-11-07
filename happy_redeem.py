import csv
import re
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config
from extractor import fetch_codes

ORDER_NUM_REGEX = re.compile(r"(SCR-\d+)")


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <brand>")
        sys.exit(1)

    brand = sys.argv[1]
    print(f"🔄 Converting to: {brand}")

    with open("happy.csv", "r", newline="") as input_file:
        csv_reader = csv.reader(input_file, delimiter="\t")

        with open(
            f"happy_{datetime.now().strftime('%m-%d-%Y_%H%M%S')}.csv", "w", newline=""
        ) as output_file:
            csv_writer = csv.writer(output_file)

            for card_num, card_pin in csv_reader:
                print(f"Redeeming card: {card_num} / {card_pin}")

                browser = webdriver.Chrome(config.CHROMEDRIVER_PATH)

                # Open the link in the browser
                browser.get("https://redeem.giftcards.com")

                code_el = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "cardCode"))
                )

                pin_el = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "cardPIN"))
                )

                code_el.send_keys(card_num)
                time.sleep(1)
                pin_el.send_keys(card_pin)
                time.sleep(1)

                button_el = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "redeem-button"))
                )

                button_el.click()

                brand_el = WebDriverWait(browser, 120).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            (
                                "//div[@class='tile' and "
                                f"contains(@aria-label, '{brand}')]"
                            ),
                        )
                    )
                )

                brand_el.click()

                amount_btn = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//input[@type='radio' and contains(@id, 'max-value')]",
                        )
                    )
                )

                amount_btn.click()

                add_to_basket_btn = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "add-to-basket"))
                )

                add_to_basket_btn.click()

                notify_close_btn = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "noty_close_button"))
                )

                notify_close_btn.click()

                checkout_btn = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "checkoutButtonWrapper"))
                )

                checkout_btn.click()

                fname_input = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//input[@name='FirstNameInput']")
                    )
                )

                fname_input.send_keys(config.HAPPY_FIRST_NAME)
                browser.find_element_by_xpath(
                    "//input[@name='LastNameInput']"
                ).send_keys(config.HAPPY_LAST_NAME)
                browser.find_element_by_xpath(
                    "//input[@name='EmailAddressInput']"
                ).send_keys(config.HAPPY_EMAIL)
                browser.find_element_by_xpath(
                    "//input[@name='ConfirmEmailAddressInput']"
                ).send_keys(config.HAPPY_EMAIL)
                browser.find_element_by_xpath(
                    "//input[@name='termsCheckbox']/following-sibling::span"
                ).click()

                place_order_btn = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "placeOrder"))
                )

                place_order_btn.click()

                confirm_btn = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "modal-confirm-button"))
                )

                confirm_btn.click()

                order_num_el = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "orderNumber"))
                )

                order_num = order_num_el.get_attribute("innerText")
                order_num = ORDER_NUM_REGEX.search(order_num).group(1)

                egc_link_el = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "download-button"))
                )

                egc_link = egc_link_el.get_attribute("href")

                print(f"==> Success! Order Number: {order_num}")

                browser.get(egc_link)

                egc_brand, egc_amount, egc_number, egc_pin = fetch_codes(browser)

                # Write the details to the CSV
                csv_writer.writerow(
                    [
                        egc_brand,
                        egc_number,
                        egc_pin,
                        egc_amount,
                        egc_link,
                        order_num,
                        card_num,
                    ]
                )

                browser.close()


if __name__ == "__main__":
    main()
