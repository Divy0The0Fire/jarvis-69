# capture audio with microphone
# process audio [...]
# convert audio to text

# capture audio with microphone

# 



import os, sys
sys.path.append(os.getcwd())

from modules.llm._groq import Groq, LLAMA_31_70B_VERSATILE
from modules.sqlqueue import SqlQueue
from modules.prompt.base import Prompt, Role, File, Image, Text, Function
from modules.vocalize.async_edgetts import fetchAudio, AudioPlayer
from datetime import datetime
from rich import print
import json
import subprocess
import asyncio



def getEmotion(emotion: str):
    jsonFile = r"data/config/emotion.config.json"
    with open(jsonFile) as f:
        data = json.load(f)
        for item in data:
            if item["emotion"] == emotion:
                return item
    return data[0]


emotionPrompt = f"""You are a language model that must express a specific emotion in your responses. Below is the emotion you need to embody:

{getEmotion('Anger')}

**Important**: You are required to respond only in this emotion. Your response must reflect the chosen emotion in every aspect, including tone, word choice, and overall expression. Any deviation from this emotion will not be acceptable.
Your response should clearly reflect the specified emotion as described above.
"""

promptTemplate = Prompt(
    template=[
        File(r"data/personality/humor_jarvis.json"),
        emotionPrompt,
        Function(lambda: f'**Date:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'),
        "my name is divyansh i like pizza"
    ],
    separator=f'\n{"-"*50}\n'
)

prompt, images = promptTemplate()


llm = Groq(model=LLAMA_31_70B_VERSATILE, systemPrompt=prompt)




voicedata = SqlQueue("data/tmp/async_google_sr.queue.db")
audioPlayer = AudioPlayer()

async def main():
    while True:
        mic = voicedata.get()
        print(mic)
        response = llm.run(mic)
        print(f"{response = }")
        audioPlayer.play(await fetchAudio(response))



with subprocess.Popen(["py", "-3.10", "modules/vocalize/async_google_sr.py"]) as process:
    asyncio.run(main())