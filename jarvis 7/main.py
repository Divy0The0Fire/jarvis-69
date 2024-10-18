import asyncio
import time
from modules.vocalize.async_edgetts import textToSpeechBytes, AudioPlayer

IMPORTS_SOUND = r"data\audio\imports.wav"
AFTER_IMPORTS_SOUND = r"data\audio\after_imports.wav"


audioPlayer = AudioPlayer()
audioPlayer.play(open(IMPORTS_SOUND, 'rb').read())
audioPlayer.setVolume(0.2)

from util.jarvis.main import process, JFunction
from typing import Optional, List, Dict, Any
from modules.database.chat_history import ChatHistoryDB




audioPlayer.play(open(AFTER_IMPORTS_SOUND, 'rb').read())
audioPlayer.setVolume(0.2)

async def jFunctionEval(jFunctions: list[JFunction]) -> list[str | None]:
    taskList = []
    for jFunction in jFunctions:
        taskList.append(asyncio.to_thread(jFunction.function))
    return await asyncio.gather(*taskList)


async def main():
    audioPlayer.play(await textToSpeechBytes("Jarvis Online!, Hello. How can I help you?"))
    while True:
        query = input(">>> ")
        result = await process(query)
        dmm = result['dmm']
        edmm = result['edmm']
        ndmm = result['ndmm']
        
        await asyncio.gather(
            jFunctionEval(ndmm),
            jFunctionEval(edmm)
        )

        dmmResult = await jFunctionEval(dmm)
        strOnlyDmmResult = list(filter(lambda x: isinstance(x, str), dmmResult))
        print(strOnlyDmmResult)
        if len(strOnlyDmmResult) == 0:
            strOnlyDmmResult = ["task completed"]
        print("Jarvis: " + ".".join(strOnlyDmmResult))
        audioPlayer.play(await textToSpeechBytes(".".join(strOnlyDmmResult)))

if __name__ == "__main__":
    asyncio.run(main())