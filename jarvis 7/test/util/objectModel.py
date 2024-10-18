import os
import sys
sys.path.append(os.getcwd())


from modules.llm._groq import Groq, LLAMA_32_90B_TEXT_PREVIEW, Role
from modules.prompt.base import Prompt, Role, File, Image, Text, Function
from util.func.emotion import Emotion, listOfEmotion
from util.func.user_notebook import UserNotebook
from rich import print
from textwrap import dedent

fun = [
    {
        "name": "chatbot",
        "description": "it is a chatbot which can answer any query. it have all the past history of user, internet, userNotebook.",
        "usage": "simply call: chatbot(query: str) query is the modified query provided by user.",
        "pattern": "chatbot(query: 'hello')"
    },
    {
        "name": "userNotebook",
        "description": "The notebook where you can store your important personal short notes of user which can be used in the future. its a internal function.",
        "usage": "it has 3 commands: add(text: str) it will add new line of text, update(line: int, text: str), delete(line: int)",
        "pattern": "userNotebook.add(text: 'hello world')"
    },
    {
        "name": "emotion",
        "description": "it is a emotion system for chatbot to express emotions. you can change the emotion depending on your mood and user previous chat. it is important to express emotion to make chatbot interactive. And it works like list of emotion. there can be many emotion at once.",
        "usage": f"it has 2 commands: add(emotion: str), remove(emotion: str), emotion is Enum of {listOfEmotion}.",
        "pattern": "emotion.remove(emotion: 'Emotion')"
    }
]


promptTemplate = f"""\
You are a decision-making model u will have last 2 queries and responses only. so make sure to add and remove userNotebook and emotions when needed.

classifies queries into the following types:

{fun}

You will not have access to output of other functions. your work is to respond to these queries. and make communication with other functions.
For multiple tasks, respond with each action separately (e.g., "function_name(arg1: 1, arg2: 2), fun_1(arg1: 1, arg2: 2)". If a query doesn't fit, respond with "chatbot(query: str)".

The current userNotebook (line number, text) is:
{UserNotebook().getText()}

The current emotions are:
{Emotion().getEmotions()}
"""

example = [
    {
        "role": "user",
        "content": "hello",
    },
    {
        "role": "assistant",
        "content": "chatbot(query: 'Hello.')",
    },
    {
        "role": "user",
        "content": "how are you",
    },
    {
        "role": "assistant",
        "content": "chatbot(query: 'How are you?')"
    }
]


llm = Groq(LLAMA_32_90B_TEXT_PREVIEW, systemPrompt=promptTemplate)

llm.messages.extend(example)

while 1:
    text = input(">>> ")
    promptTemplate = dedent(f"""\
You are a decision-making model u will have last 2 queries and responses only. so make sure to add and remove userNotebook and emotions when needed.

classifies queries into the following types:

{fun}

You will not have access to output of other functions. your work is to respond to these queries. and make communication with other functions.
For multiple tasks, respond with each action separately (e.g., "function_name(arg1: 1, arg2: 2), fun_1(arg1: 1, arg2: 2)". If a query doesn't fit, respond with "chatbot(query: str)".

The current userNotebook (line number, text) is:
{UserNotebook().getText()}

The current emotions are:
{Emotion().getEmotions()}
    """)
    print(promptTemplate)
    llm.messages[0] = {"role": "system", "content": promptTemplate}
    print(llm.run(text))
    