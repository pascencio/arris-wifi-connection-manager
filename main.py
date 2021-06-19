from copy import Error
import logging
from logging.handlers import TimedRotatingFileHandler
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(filename="arris.log",
                                   when="d",
                                   interval=1,
                                   backupCount=5)
formatter = logging.Formatter(
    "[%(levelname)s]:[%(asctime)s]:[%(name)s] - %(message)s")

handler.setFormatter(formatter)

LOGGER.addHandler(handler)

DEFAULT_WAIT_TIME = 60


def is_checked(driver, element_id):
    checked = driver.execute_script(
        ("return document.getElementById('{}').checked").format(element_id)
    )
    return checked


def logout(driver):
    try:
        logout_anchor = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#nav > li:nth-child(3) > a:nth-child(1)"))
        )
        logout_anchor.click()
    except Error as e:
        LOGGER.error("Error closing sessión: ", exc_info=e)


def main(command):
    console_host = os.environ["ARRIS_CONSOLE_HOST"]
    console_user = os.environ["ARRIS_CONSOLE_USER"]
    console_password = os.environ["ARRIS_CONSOLE_PASSWORD"]
    client_mac_address = os.environ["CLIENT_MAC_ADDRESS"]
    executable_path = os.environ["EXECUTABLE_PATH"]
    os.environ["PATH"] = "{}:{}".format(
        os.environ["PATH"],
        executable_path
    )
    dry_run = os.environ["DRY_RUN"] == "1"
    headless = os.environ["HEADLESS"] == "1"
    disable_wifi = command == "disable"
    enable_wifi = command == "enable"
    options = webdriver.ChromeOptions()
    options.headless = headless
    driver = webdriver.Chrome(options=options)
    driver.get(console_host)
    try:
        user_input = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located((By.ID, "UserName"))
        )
        user_input.send_keys(console_user)
        password_input = driver.find_element_by_id("Password")
        password_input.send_keys(console_password)
        apply_button = driver.find_element_by_css_selector(
            "input[class=submitBtn]"
        )
        apply_button.click()
        LOGGER.info("Starting new session")
        lan_settings_anchor = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 ".tabNavigation > li:nth-child(3) > a:nth-child(1)")
            )
        )
        lan_settings_anchor.click()
        LOGGER.info("Session started. Accesing to LAN settings")
        lan_dhcp_anchor = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 ".sidenav > li:nth-child(3) > a:nth-child(1)")
            )
        )
        LOGGER.info("Accesing to LAN client list")
        lan_dhcp_anchor.click()
        WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located(
                (By.ID,
                 "FixedDHCPClients")
            )
        )
        mac_addresses = driver.find_elements_by_css_selector(
            "tr[class=dataRow]>td:nth-child(4)"
        )
        LOGGER.info("Checking client status: [mac_address='%s']",
                    client_mac_address)
        index = -1
        for mac_address in mac_addresses:
            index += 1
            if mac_address.text == client_mac_address:
                break
        status = ""
        if index > 0:
            LOGGER.info("Client founded at: [index='%s']", index)
            client_status = driver.find_elements_by_css_selector(
                "tr[class=dataRow]>td:nth-child(5)"
            )
            status = client_status[index].text
        if status == "Offline":
            LOGGER.info("Client is OFFLINE")
            wifi_24_anchor = driver.find_element_by_css_selector(
                ".tabNavigation > li:nth-child(4) > a:nth-child(1)"
            )
            LOGGER.info("Accesing to WIFI 2.4G settings")
            wifi_24_anchor.click()
            enable_wireless_checkbox = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
                EC.presence_of_element_located(
                    (By.ID,
                     "EnableWireless")
                )
            )
            submit_changes = False
            if is_checked(driver, "EnableWireless") and disable_wifi:
                LOGGER.info("Disabling 2.4G WIFI")
                submit_changes = True
            elif not is_checked(driver, "EnableWireless") and enable_wifi:
                LOGGER.info("Enabling 2.4G WIFI")
                submit_changes = True
            if submit_changes:
                enable_wireless_checkbox.click()
                if disable_wifi:
                    time.sleep(10)
                    alert = driver.switch_to.alert
                    alert.accept()
                if not dry_run:
                    submit_button = driver.find_element_by_class_name(
                        "submitBtn")
                    submit_button.click()
            wifi_50_anchor = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     ".tabNavigation>li:nth-child(5)>a:nth-child(1)")
                )
            )
            wifi_50_anchor.click()
            LOGGER.info("Accesing to WIFI 5G settings")
            enable_wireless_checkbox = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
                EC.presence_of_element_located(
                    (By.ID,
                     "EnableWireless")
                )
            )
            submit_changes = False
            if is_checked(driver, "EnableWireless") and disable_wifi:
                submit_changes = True
                LOGGER.info("Disabling 5G WIFI")
            elif not is_checked(driver, "EnableWireless") and enable_wifi:
                LOGGER.info("Enabling 5G WIFI")
                submit_changes = True
            if submit_changes:
                enable_wireless_checkbox.click()
                if disable_wifi:
                    time.sleep(10)
                    alert = driver.switch_to.alert
                    alert.accept()
                if not dry_run:
                    submit_button = driver.find_element_by_class_name(
                        "submitBtn")
                    submit_button.click()
        elif status == "Online":
            LOGGER.info("Connection status: ONLINE")
        else:
            LOGGER.warning("Client status not founded")
        time.sleep(60)
        driver.save_screenshot('success.png')
    except Exception as e:
        driver.save_screenshot('error.png')
        LOGGER.error("Error on disable/enable WIFI", exc_info=e)
    finally:
        logout(driver)
        driver.quit()


if __name__ == "__main__":
    command = sys.argv[1]
    main(command)
