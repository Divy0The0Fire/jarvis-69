import os, sys
import time

sys.path.append(os.getcwd())

from modules.llm._groq import Groq, LLAMA_32_90B_TEXT_PREVIEW
from modules.llm._cohere import Cohere, COMMAND_R_PLUS
from modules.prompt.base import Prompt, Role, File, Image, Text, Function
from modules.database.chat_history import ChatHistoryDB

from util.func.chatbot import Chatbot
from util.func.user_notebook import UserNotebook
from util.func.emotion import Emotion

from util.model.dmm import systemPromptTemplate as dmmSystemPrompt
from util.model.edmm import systemPromptTemplate as edmmSystemPrompt
from util.model.ndmm import systemPromptTemplate as ndmmSystemPrompt

from dataclasses import dataclass
from dotenv import load_dotenv
from rich import print
from typing import Optional, Callable
from webbrowser import open as open_browser
import asyncio

load_dotenv()

# ------------------------------------------------ #

emotion = Emotion()
userNotebook = UserNotebook()
chatbotInstance = Chatbot(
    llm=Groq(
        LLAMA_32_90B_TEXT_PREVIEW,
        maxTokens=4096,
        logFile=os.getenv("DATA_DIR") + r"/log/chatbot.log"
        ),
    profile=r"data\personality\humor_jarvis.json",
    emotion=emotion,
    userNotebook=userNotebook
)
historyDb = ChatHistoryDB(r"data\sql\chat_history.sql")

# ------------------------------------------------ #


# ------------------------------------------------ #

dmmLLM = Cohere(COMMAND_R_PLUS, maxTokens=4096, logFile=os.getenv("DATA_DIR") + r"/log/dmm.log")
edmmLLM = Groq(LLAMA_32_90B_TEXT_PREVIEW, maxTokens=4096, logFile=os.getenv("DATA_DIR") + r"/log/eddm.log")
ndmmLLM = Groq(LLAMA_32_90B_TEXT_PREVIEW, maxTokens=4096, logFile=os.getenv("DATA_DIR") + r"/log/nddm.log")

# ------------------------------------------------ #


historyDb.getLastNMessages(int(os.getenv("JARVIS_HISTORY_LIMIT")))

@dataclass
class JFunction:
    name: str
    function: Function
    priority: Optional[int] = None # lower number = higher priority


def doPass(isPass: bool) -> None:
    return None


def dmm(query: str) -> list[JFunction]:
    dmmLLM.messages = []
    dmmLLM.addMessage(Role.system, dmmSystemPrompt.prompt)
    response = dmmLLM.run(query)

    functionList: list[JFunction] = []

    def chatbot(prompt: str):
        functionList.append(
            JFunction(
                name="chatbot",
                function=Function(
                    chatbotInstance.run,
                    prompt=prompt,
                ),
                priority=1
            )
        )

    def askUser(query: str):
        functionList.append(
            JFunction(
                name="askUser",
                function=Function(
                    print,
                    "askUser : " + query,
                ),
                priority=1
            )
        )
    
    def url(url: str):
        functionList.append(
            JFunction(
                name="url",
                function=Function(
                    open_browser,
                    url,
                ),
                priority=1
            )
        )
    
    def pythonDon(query: str):
        functionList.append(
            JFunction(
                name="pythonDon",
                function=Function(
                    print,
                    "pythonDon : " + query,
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

def edmm(query: str) -> list[JFunction]:
    edmmLLM.messages = []
    edmmLLM.addMessage(Role.system, edmmSystemPrompt.prompt)
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

def ndmm(query: str) -> list[JFunction]:
    ndmmLLM.messages = []
    ndmmLLM.addMessage(Role.system, ndmmSystemPrompt.prompt)
    response = ndmmLLM.run(query)

    functionList: list[JFunction] = []
    print(f"by ndmm: {response = }")
    
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


def rawToJson(rawMessageList: list[dict[str, str]]) -> list[dict[str, str]]:
    return rawMessageList

def jsonToPrompt(rawMessageList: list[dict[str, str]]) -> str:
    prompt = ""
    for message in rawMessageList:
        if message['role'] == 'system':
            continue
        if message['role'] == 'assistant':
            prompt += f"{message['role']}: {message['content'][:100]} ...\n"
        else:
            prompt += f"{message['role']}: {message['content']}\n"
    return prompt

async def process(query: str) -> list[JFunction]:
    rawMessageList = historyDb.getLastNMessages(
        int(os.getenv("JARVIS_HISTORY_LIMIT", 20)),
        projections=['role', 'content']
        )

    messageList = rawToJson(rawMessageList)
    chatPrompt = jsonToPrompt(messageList)
    chatPromptQuery = "\nCurrent Query: " + query
    
    dmmTask = asyncio.to_thread(
        dmm,
        chatPromptQuery
    )
    
    ndmmTask = asyncio.to_thread(
        ndmm,
        chatPrompt + chatPromptQuery
    )
    
    edmmTask = asyncio.to_thread(
        edmm,
        chatPrompt + chatPromptQuery
    )
    C = time.time()
    dmmResult, ndmmResult, edmmResult = await asyncio.gather(dmmTask, ndmmTask, edmmTask)

    return {
        "dmm": dmmResult,
        "edmm": edmmResult,
        "ndmm": ndmmResult
    }





if __name__ == "__main__":
    while True:
        try:
            print(asyncio.run(process(input(">>> "))))
        except Exception as e:
            print(f"An error occurred: {e}")
