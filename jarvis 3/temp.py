from modules.llm._groq import Groq, LLAMA_31_70B_VERSATILE
from modules.prompt.base import Prompt, Role, File, Image, Text, Function
from datetime import datetime
from rich import print
from time import sleep
# llm = Groq(
#     model=LLAMA_31_70B_VERSATILE,
#     systemPrompt="you only have to answer math expressions. and ignore everything else. u have to reply in json formate only.",
#     )

# resp = llm.run("2+2")
# print(resp)

# TARGET IS TO CREATE A PROMPT FOR CHAT BOT.
"""
- personal details
- current datetime
- weather
- schedule
"""

def weather():
    # simulating the delay
    sleep(1)
    return "sunny"

def slow_function_1():
    sleep(2)  # Simulate 2 seconds of work
    return "Result from slow_function_1"

def slow_function_2():
    sleep(3)  # Simulate 3 seconds of work
    return "Result from slow_function_2"


promptTemplate = Prompt(
    template=[
        File(r"personaldetails.txt"),
        Function(datetime.now),
        Function(lambda: f"weather: {weather()}"),
        "i like to eat pizza"
    ],
    separator=f'\n{"-"*50}\n'
)

# prompt, images = promptTemplate.prompt

# print(prompt)
from time import time as t

startTime = t()

print(
    f"""
    {slow_function_1()}
    {slow_function_1()}
    {slow_function_1()}
    {slow_function_1()}
    {slow_function_2()}
    {slow_function_2()}
    {slow_function_2()}
    """
)

print("time taken in seconds", t() - startTime)

