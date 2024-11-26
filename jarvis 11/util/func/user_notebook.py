import os
import logging
from pythonjsonlogger import jsonlogger
from rich.logging import RichHandler
from dotenv import load_dotenv
from hashlib import sha256
from typing import Optional
try:
    from data.config.config import userNotebook
except ImportError:
    import sys
    sys.path.append(os.getcwd())
    from data.config.config import userNotebook


load_dotenv()
TMP_DIR = os.getenv("TMP_DIR", "/tmp")
DATA_DIR = os.getenv("DATA_DIR")

logger = logging.getLogger(__file__.split("/")[-1])
logger.setLevel(logging.INFO)  # Set default log level
json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(name)s %(funcName)s')
rich_handler = RichHandler()
logger.addHandler(rich_handler)
LOG_FILE = os.path.join(DATA_DIR, "log", "user_notebook.log")
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(json_formatter)
logger.addHandler(file_handler)




class UserNotebook:
    def __init__(self):
        logger.info(
            {
                "action": "init",
                "message": "initializing user_notebook",
                "userNotebook": userNotebook,
            }
        )
    def addRecord(self, textLine: str) -> None:
        logger.info(
            {
                "action": "addRecord",
                "message": "adding record",
                "textLine": sha256(textLine.encode()).digest().hex(),
            }
        )
        userNotebook.addRecord(textLine)
    
    def updateRecord(self, recordId: int, newTextLine: str) -> None:
        logger.info(
            {
                "action": "updateRecord",
                "message": "updating record",
                "recordId": recordId,
                "newTextLine": sha256(newTextLine.encode()).digest().hex(),
            }
        )
        userNotebook.updateRecord(recordId, newTextLine)
    
    def deleteRecord(self, recordId: int) -> None:
        logger.info(
            {
                "action": "deleteRecord",
                "message": "deleting record",
                "recordId": recordId,
            }
        )
        userNotebook.deleteRecord(recordId)

    def getText(self, start: Optional[int] = None, end: Optional[int] = None) -> str:
        logger.info(
            {
                "action": "getText",
                "message": "getting text",
                "start": start,
                "end": end,
            }
        )
        return userNotebook.getText(start, end)


if __name__ == "__main__":
    userNotebook_ = UserNotebook()
    userNotebook_.addRecord("user Name is Divyansh Shukla")
    # userNotebook_.addRecord("hello world 2")
    # userNotebook_.addRecord("hello world 3")
    # userNotebook_.addRecord("hello world 4")
    print(userNotebook_.getText())