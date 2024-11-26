#pip install selenium

import os
import sys
import logging

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from pythonjsonlogger import jsonlogger
from rich.logging import RichHandler

load_dotenv()

try:
    from modules.sqlqueue import SqlQueue
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(__file__) + "/../../")
    from modules.sqlqueue import SqlQueue


SPEECHRECOGNITION_LANGUAGE = os.getenv("SPEECHRECOGNITION_LANGUAGE", "en-US")
TMP_DIR = os.getenv("TMP_DIR", "/tmp")
DATA_DIR = os.getenv("DATA_DIR")

logger = logging.getLogger(__file__.split("/")[-1])
logger.setLevel(logging.INFO)  # Set default log level
json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(name)s %(funcName)s')
rich_handler = RichHandler()
logger.addHandler(rich_handler)
LOG_FILE = os.path.join(DATA_DIR, "log", "async_js_sr.log")
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(json_formatter)
logger.addHandler(file_handler)


Queue = SqlQueue("data/tmp/async_js_sr.queue.db")

chrome_options = webdriver.EdgeOptions()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--headless=new")
driver = webdriver.Edge(options=chrome_options)

logger.info("browser Initialized")

website = f"{os.getcwd()}/data/html/js_sr.html?lang=" + SPEECHRECOGNITION_LANGUAGE

print(website)
driver.get(website)
logger.info("website loaded")

def listen():
    driver.find_element(by=By.ID, value='end').click()
    driver.find_element(by=By.ID, value='start').click()
    while 1:
        text=driver.find_element(by=By.ID, value='output').text
        if text != "":
            Queue.put(text)
            driver.find_element(by=By.ID, value='end').click()
            return text

if __name__=="__main__":
    logger.info("Starting main loop")
    while 1:
        listen()