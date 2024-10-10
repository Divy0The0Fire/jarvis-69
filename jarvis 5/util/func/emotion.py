import os
import json
import logging
from pythonjsonlogger import jsonlogger
from rich.logging import RichHandler
from dotenv import load_dotenv

try:
    from data.config.config import sqDict
    from modules.prompt.type import File
except ImportError:
    import sys
    sys.path.append(os.getcwd())
    from data.config.config import sqDict
    from modules.prompt.type import File

load_dotenv()
DATA_DIR = os.getenv("DATA_DIR")

logger = logging.getLogger(__file__.split("/")[-1])
logger.setLevel(logging.INFO)  # Set default log level
json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(name)s %(funcName)s')
rich_handler = RichHandler()
logger.addHandler(rich_handler)
LOG_FILE = os.path.join(DATA_DIR, "log", "emotion.log")
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(json_formatter)
logger.addHandler(file_handler)


emotionConfigFile = r"data/config/emotion.config.json"

emotionListOfDict: list[dict[str, str]] = json.loads(
    File(emotionConfigFile).text
)

listOfEmotion: list[str] = [x["emotion"] for x in emotionListOfDict]
promptOfEmotion: dict[str, dict[str, str]] = {
    x["emotion"]: x for x in emotionListOfDict
}


class Emotion:
    def __init__(self) -> None:
        logger.info(
            {
                "action": "init",
                "message": "initializing emotion system",
                "sqDict[emotion]": sqDict.get("emotion", None),
                "countOfEmotion": len(emotionListOfDict),
            }
        )

    def getEmotions(self) -> list[str]:
        """
        return list of emotion in current system tray.
        """
        val = sqDict.get("emotion", None)
        if not val:
            sqDict["emotion"] = []
            val = []

        logger.info(
            {
                "action": "getEmotions",
                "message": "return list of emotion in current system tray",
                "sqDict[emotion]": val,
            }
        )

        return val

    def addEmotion(self, new_emotion: str) -> None:
        """
        add emotion to current system tray.
        """
        current_emotions: list = sqDict.get("emotion", [])
        
        if new_emotion not in listOfEmotion:
            logger.error(
                {
                    "action": "addEmotion",
                    "message": "add emotion to current system tray",
                    "error": "emotion not Exist in config",
                    "new_emotion": new_emotion,
                    "listOfEmotion": listOfEmotion,
                }
            )
            return
        
        if new_emotion in current_emotions:
            logger.warning(
                f"emotion already exists in system tray: {new_emotion}"
            )
            return
        current_emotions.append(new_emotion)
        sqDict["emotion"] = current_emotions
        logger.info(
            {
                "action": "addEmotion",
                "message": "add emotion to current system tray",
                "emotion": current_emotions,
            }
        )

    def removeEmotion(self, remove_emotion: str) -> None:
        """
        remove emotion from current system tray.
        """
        current_emotions: list = sqDict.get("emotion", [])
        
        if remove_emotion not in listOfEmotion:
            logger.error(
                {
                    "action": "removeEmotion",
                    "message": "remove emotion from current system tray",
                    "error": "emotion not Exist in config",
                    "listOfEmotion": listOfEmotion,
                    "remove_emotion": remove_emotion,
                }
            )
            return
        
        if remove_emotion not in current_emotions:
            logger.warning(
                {
                    "action": "removeEmotion",
                    "message": "remove emotion from current system tray",
                    "emotion": current_emotions,
                    "error": "emotion not found",
                    "sqDict[emotion]": current_emotions,
                    "remove_emotion": remove_emotion,
                }
            )
            return
        current_emotions.remove(remove_emotion)
        sqDict["emotion"] = current_emotions
        logger.info(
            {
                "action": "removeEmotion",
                "message": "remove emotion from current system tray",
                "emotion": current_emotions,
            }
        )

    def promptJson(self, indent: int = 0) -> str:
        """
        prompt for emotion in current system tray.
        """
        Json = []
        _emotion = sqDict.get("emotion", [])
        for emotion in _emotion:
            if emotion in promptOfEmotion:
                Json.append(promptOfEmotion[emotion])
        return json.dumps(Json, indent=indent)


if __name__ == "__main__":
    from rich import print
    emotion = Emotion()
    print(emotion.getEmotions())
    emotion.addEmotion("Excitementt")
    print(emotion.getEmotions())
    print(emotion.promptJson(indent=4))
