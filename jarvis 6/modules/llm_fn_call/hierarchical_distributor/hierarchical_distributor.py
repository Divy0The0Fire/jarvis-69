import os
import sys
import json

sys.path.append(os.path.dirname(__file__)+"/../")
sys.path.append(os.getcwd())

from modules.llm._cohere import Cohere, COMMAND_R, Model, ModelType, Role
from rich import print
from blueprint.fn_doc import Fn, generateSystemPrompt, extractJSON
 

functions = [
    Fn(
        name="whatIsTime",
        description="Fetches the current time.",
        parameters={},
        example_output="2022-10-10T23:00:00Z"
    ),
    Fn(
        name="wikiSearch",
        description="Searches Wikipedia for a specific query.",
        parameters={"query": "string"},
        example_input={"query": "Bitcoin"},
        example_output="Bitcoin is a cryptocurrency that was invented in 2008 by an unknown person or group of people."
    ),
    Fn(
        name="openApp",
        description="Opens an application. on windows 64bit using AppOpener module. returns true on success",
        parameters={"app": "string"},
        example_input={"app": "Google Chrome"},
        example_output=True
    ),
    Fn(
        name="playMusic",
        description="Plays a music search query on yt and plays it.",
        parameters={"query": "string"},
        example_input={"query": "Coldplay"},
        example_output="Coldplay - Paradise"
    )
]



systemPrompt = generateSystemPrompt(functions)

print(systemPrompt)

print("-"*100)
llm = Cohere(
    model=COMMAND_R,
    systemPrompt=systemPrompt
    )


if __name__ == "__main__":
    while True:
        query = input("Query: ")
        if query == "exit":
            break
        response = llm.run(query, save=False)
        llm.addMessage(
            Role.user,
            response
        )
        llm.addMessage(
            Role.assistant,
            json.dumps(extractJSON(response))
        )
        print("RAW: ", response)
        print("JSON: ", extractJSON(response))

