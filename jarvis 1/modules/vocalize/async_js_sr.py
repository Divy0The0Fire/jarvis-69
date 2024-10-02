#pip install selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import sys
from dotenv import load_dotenv
load_dotenv()

try:
    from modules.sqlqueue import SqlQueue
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(__file__) + "/../../")
    from modules.sqlqueue import SqlQueue

Queue = SqlQueue("data/tmp/async_js_sr.queue.db")

chrome_options = webdriver.EdgeOptions()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--headless=new")
driver = webdriver.Edge(options=chrome_options)

website = f"{os.getcwd()}/data/html/js_sr.html?lang=" + os.getenv("SPEECHRECOGNITION_LANGUAGE", "en-US")

print(website)
driver.get(website)

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
    while 1:
        listen()