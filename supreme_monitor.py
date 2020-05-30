import os
import sys
import time
import six
import pause
import ssl
import argparse
import logging.config
import smtplib
from selenium import webdriver
from dateutil import parser as date_parser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [PID %(process)d] [Thread %(thread)d] [%(levelname)s] [%(name)s] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "console"
        ]
    }
})

LOGGER = logging.getLogger()

def run(driver, url, sleep_time, gmail_from, mail_to, gmail_password):
    driver.maximize_window()
    mail_text = "Your link is ONLINE\n" + url
    while True:
        try:
            LOGGER.info("Requesting page: " + url)
            driver.get(url)
        except TimeoutException:
            LOGGER.info("Page load timed out but continuing anyway")
        res = check_exists_by_xpath("//b[@class='button sold-out']")
        if res == False:
            LOGGER.info("NOW INSTOCK... SENDING MAIL TO " + mail_to)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.ehlo()
            server.login(gmail_from, gmail_password)
            server.sendmail(gmail_from, mail_to, mail_text)
            server.quit()
            LOGGER.info("Email sent")
            break
        else:
            LOGGER.info("STILL SOLDOUT")
        time.sleep(sleep_time)
    driver.quit()


def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

if __name__ == "__main__":
    text = """
    _____________________________________________
    !\__________________________________________/!\ 
    !!  ___ _   _ _ __  _ __ ___ _ __ ___   ___  !! \  
    !! / __| | | | '_ \| '__/ _ \ '_ ` _ \ / _ \ !!  \ 
    !! \__ \ |_| | |_) | | |  __/ | | | | |  __/ !!  !
    !! |___/\__,_| .__/|_|  \___|_| |_| |_|\___| !!  !
    !!           | |          _ __ ___           !!  !
    !!           |_|         | '_ ` _ \   ___    !!  !
    !!                       | | | | | | | _ |   !!  !
    !!                       |_| |_| |_| |___|   !!  /
    !!___________________________________________!! /
    !/___________________________________________\!/
       __\___________________________________/__/!_    By Nicobar
    """
    print(text)
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://www.supremenewyork.com/shop/shoes/ndrgpvxhm/cxypn34k5", help="Url to monitor (Default is for AF1 White SUP: https://www.supremenewyork.com/shop/shoes/ndrgpvxhm/cxypn34k5)")
    parser.add_argument("--gmail-from", required=True, help="Gmail account for sending the email")
    parser.add_argument("--gmail-password", required=True, help="Gmail account password")
    parser.add_argument("--mail-to", required=True, help="Mail destination account")
    parser.add_argument("--sleep-time", default=10, help="Time to sleep between URL checks")
    parser.add_argument("--driver-type", default="firefox", choices=("firefox", "chrome"), help="Selected driver to use (chrome may not be working) Default: firefox")
    parser.add_argument("--headless", action="store_true", help="Do not show the browser window")
    args = parser.parse_args()

    driver = None
    if args.driver_type == "firefox":
        options = webdriver.FirefoxOptions()
        if args.headless:
            options.add_argument("--headless")
        if sys.platform == "darwin":
            executable_path = "./bin/geckodriver_mac"
        elif "linux" in sys.platform:
            executable_path = "./bin/geckodriver_linux"
        else:
            raise Exception("Unsupported operating system. Please add your own Selenium driver for it.")
        driver = webdriver.Firefox(executable_path=executable_path, firefox_options=options, log_path=os.devnull)
    elif args.driver_type == "chrome":
        options = webdriver.ChromeOptions()
        if args.headless:
            options.add_argument("headless")
        if sys.platform == "darwin":
            executable_path = "./bin/chromedriver_mac"
        elif "linux" in sys.platform:
            executable_path = "./bin/chromedriver_linux"
        else:
            raise Exception("Unsupported operating system. Please add your own Selenium driver for it.")
        driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)

    run(driver=driver, url=args.url, sleep_time=args.sleep_time, gmail_from=args.gmail_from, mail_to=args.mail_to, gmail_password=args.gmail_password)
