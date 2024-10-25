import os, sys
import time

sys.path.append(os.getcwd())

from modules.prompt.base import Prompt, Role, File, Image, Text, Function
from modules.llm.base import ModelType, LLM

from util.func.chatbot import Chatbot
from util.func.user_notebook import UserNotebook
from util.func.emotion import Emotion
from util.func.url_open import url as url_func
from util.func.ss_base64 import screenshot

from util.model.dmm import systemPromptTemplate as dmmSystemPrompt
from util.model.edmm import systemPromptTemplate as edmmSystemPrompt
from util.model.ndmm import systemPromptTemplate as ndmmSystemPrompt

from data.config.config import (
    dmmLLM, edmmLLM, ndmmLLM, codeBrew,
    chatBotLLM, userNotebook, profile, historyDb,
    dmmHistoryDb, edmmHistoryDb, ndmmHistoryDb,
    SCREENSHOT
)

from dataclasses import dataclass
from dotenv import load_dotenv
from rich import print
from typing import Optional, Callable
from textwrap import dedent

import asyncio

from nara.extra.tools import timeIt
load_dotenv()

# ------------------------------------------------ #


# ------------------------------------------------ # 

# ------------------------------------------------ #

emotion = Emotion()
userNotebook = UserNotebook()
chatbotInstance = Chatbot(
    llm=chatBotLLM,
    profile=profile,
    emotion=emotion,
    userNotebook=userNotebook,
    logFile=os.getenv("DATA_DIR") + r"/log/chatbotInstance.log"
)

# ------------------------------------------------ #

# Extending system prompts


if SCREENSHOT and chatBotLLM.model.typeof == ModelType.textandimage:
    chatbotInstance.systemPrompt.template.append(
        Function(
            lambda: Image(
                    text=dedent(
                        """\
                        This is a screenshot of the user's desktop.
                        When the user mentions 'screen', 'what's on the screen', or asks 'what/how is this',
                        they are referring to this image. Always analyze and describe the image content.
                        Never state that you cannot see an image, as it is provided here.
                        Describe what you see in detail, including any visible applications, icons, or content.
                        If asked about specific elements, focus on those areas of the image.
                        """
                    ),
                url=screenshot(),
            ),
        )
    )
    print("Screenshot is enabled and chatbot model is text and image")
else:
    print("Screenshot is not enabled or chatbot model is not text and image")


# ------------------------------------------------ #



@dataclass
class JFunction:
    name: str
    function: Function
    priority: Optional[int] = None # lower number = higher priority

def doPass(isPass: bool) -> None:
    return None


# TODO: DMMS CAN BE BETTERLY EVALUATED BY USING PARSER IN modules.llm_fn_call.parser.one_param

@timeIt
def dmm(query: str, chatPrompt: Optional[str] = None) -> list[JFunction]:
    dmmLLM.messages = []

    systemPrompt, imagePrompt = dmmSystemPrompt.fastpromptWithImages
    dmmLLM.addMessage(Role.system, systemPrompt)
    dmmLLM.messages.extend(imagePrompt)

    if chatPrompt is not None:
        dmmLLM.addMessage(Role.user, chatPrompt)

    response = dmmLLM.run(query)

    functionList: list[JFunction] = []

    def chatbot(prompt: str):
        functionList.append(
            JFunction(
                name="chatbot",
                function=Function(
                    chatbotInstance.run,
                    prompt=prompt,
                    messages=historyDb.getLastNMessages(
                        n=int(os.getenv("JARVIS_HISTORY_LIMIT", 20)),
                        projections=["role", "content"]
                    )[::-1]
                ),
                priority=1
            )
        )

    def askUser(query: str):
        functionList.append(
            JFunction(
                name="askUser",
                function=Function(
                    codeBrew.print,
                    query,
                ),
                priority=1
            )
        )

    def url(url: str):
        functionList.append(
            JFunction(
                name="url",
                function=Function(
                    url_func,
                    url=url,
                ),
                priority=1
            )
        )

    def pythonDon(query: str):
        functionList.append(
            JFunction(
                name="pythonDon",
                function=Function(
                    codeBrew.run,
                    query,
                ),
                priority=1
            )
        )

    try:
        eval(response)
    except Exception as e:
        print(e)
        functionList.append(
            JFunction(
                name="printError",
                function=Function(
                    print,
                    "error : " + str(e),
                ),
                priority=1
            )
        )
    return functionList

@timeIt
def edmm(query: str, chatPrompt: Optional[str] = None) -> list[JFunction]:
    edmmLLM.messages = []
    
    systemPrompt, imagePrompt = edmmSystemPrompt.fastpromptWithImages
    edmmLLM.addMessage(Role.system, systemPrompt)
    edmmLLM.messages.extend(imagePrompt)
    
    if chatPrompt is not None:
        edmmLLM.addMessage(Role.user, chatPrompt)

    response = edmmLLM.run(query)

    functionList: list[JFunction] = []

    def addEmotion(new_emotion: str):
        functionList.append(
            JFunction(
                name="addEmotion",
                function=Function(
                    emotion.addEmotion,
                    new_emotion=new_emotion
                ),
                priority=1
            )
        )

    def removeEmotion(remove_emotion: str):
        functionList.append(
            JFunction(
                name="removeEmotion",
                function=Function(
                    emotion.removeEmotion,
                    remove_emotion=remove_emotion
                ),
                priority=1
            )
        )

    try:
        eval(response)
    except Exception as e:
        print(e)
        functionList.append(
            JFunction(
                name="printError",
                function=Function(
                    print,
                    "error : " + str(e),
                ),
                priority=1
            )
        )
    return functionList

@timeIt
def ndmm(query: str, chatPrompt: Optional[str] = None) -> list[JFunction]:
    ndmmLLM.messages = []

    systemPrompt, imagePrompt = ndmmSystemPrompt.fastpromptWithImages
    ndmmLLM.addMessage(Role.system, systemPrompt)
    ndmmLLM.messages.extend(imagePrompt)
    
    if chatPrompt is not None:
        ndmmLLM.addMessage(Role.user, chatPrompt)
    
    response = ndmmLLM.run(query)

    functionList: list[JFunction] = []
    
    def addRecord(textLine: str):
        functionList.append(
            JFunction(
                name="addRecord",
                function=Function(
                    userNotebook.addRecord,
                    textLine=textLine,
                ),
                priority=1
            )
        )
    
    def deleteRecord(recordId: int):
        functionList.append(
            JFunction(
                name="deleteRecord",
                function=Function(
                    userNotebook.deleteRecord,
                    recordId=recordId,
                ),
                priority=1
            )
        )
    
    def updateRecord(record: dict[int, str]):
        recordId, newTextLine = list(record.items())[0]
        functionList.append(
            JFunction(
                name="updateRecord",
                function=Function(
                    userNotebook.updateRecord,
                    recordId=recordId,
                    newTextLine=newTextLine
                ),
                priority=1
            )
        )

    try:
        eval(response)
    except Exception as e:
        print(e)
        functionList.append(
            JFunction(
                name="printError",
                function=Function(
                    print,
                    "error : " + str(e),
                ),
                priority=1
            )
        )

    return functionList

async def process(query: str) -> list[JFunction]:
    print(f"{query = }")
    
    dmmTask = asyncio.to_thread(
        dmm,
        query
    )

    ndmmTask = asyncio.to_thread(
        ndmm,
        query
    )
    
    edmmTask = asyncio.to_thread(
        edmm,
        query
    )
    C = time.time()
    dmmResult, ndmmResult, edmmResult = await asyncio.gather(dmmTask, ndmmTask, edmmTask)
    return {
        "dmm": dmmResult,
        "edmm": edmmResult,
        "ndmm": ndmmResult,
        "timeTaken": time.time() - C
    }


if __name__ == "__main__":
    while True:
        try:
            print(asyncio.run(process(input(">>> "))))
        except Exception as e:
            print(f"An error occurred: {e}")
