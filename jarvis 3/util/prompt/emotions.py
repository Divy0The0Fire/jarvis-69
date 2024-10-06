import json

emotionsJsonFile = r"data/config/emotion.config.json"

emotions = json.load(open(emotionsJsonFile))

listOfEmotions = [emotion["emotion"] for emotion in emotions]

