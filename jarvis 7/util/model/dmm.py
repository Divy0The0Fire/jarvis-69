"Decision Making Model"
import os, sys
sys.path.append(os.getcwd())

from modules.llm_fn_call.blueprint.one_param import Fn, generateSystemPrompt
from modules.prompt.base import Prompt, Role, File, Image, Text, Function
from textwrap import dedent
from rich import print

functions = [
    Fn(
        name="askUser",
        description=dedent(
            """
            Use this function when the user's instructions are unclear, or if you need 
            further clarification before proceeding. For example, if you are uncertain 
            about what the user wants or if there are missing details that could affect 
            the outcome, you can ask a follow-up question for clarity. Pass the question 
            you wish to ask the user as the input parameter 'query', and the function 
            will return the user's response.
            example:
            user: open

            it was an incomplete question by the user it is not clear what the user wants.
            """
        ),
        parameter={"query": "string"}
    ),
    Fn(
        name="chatbot",
        description=dedent(
            """
            Use this function when the user is asking a general or real-time question that 
            can be answered by an AI-powered chatbot. This chatbot has access to the 
            internet, user's history, user's camera, and screenshot. allowing it to retrieve the latest information and handle a wide 
            range of topics, including questions related to current events, general knowledge, 
            or previous user interaction history.
            Pass the user's query as the input parameter 'prompt' to get an appropriate response.
            """
        ),
        parameter={"prompt": "string"}
    ),
    Fn(
        name="url",
        description=dedent(
            """
            Call this function only when you are confident that the user explicitly 
            wants you to open a specific URL. You must be certain of the user's intent 
            before invoking this function. Provide the exact URL as the input parameter 'url' 
            to proceed with opening it.
            """
        ),
        parameter={"url": "string"}
    ),
    Fn(
        name="pythonDon",
        description=dedent(
            """
            Used to automate tasks in Python.
            Invoke this function when the user's task requires Python code execution 
            or any task that can be automated using Python. This function utilizes 
            an advanced AI named 'pythonDon' capable of generating and running Python 
            code for a wide variety of tasks, including data processing, file manipulation, 
            and automation. Although 'pythonDon' may be slower, it ensures accurate task 
            completion. Pass the specific task or problem as the input parameter 'query'.
            """
        ),
        parameter={"query": "string"}
    )
]


systemPromptTemplate = Prompt(
    template=[
        generateSystemPrompt(functions)
    ]
)

if __name__ == "__main__":
    from modules.llm._cohere import Cohere, COMMAND_R_PLUS, Model, ModelType, Role
    llm = Cohere(model=COMMAND_R_PLUS, systemPrompt=systemPromptTemplate.prompt)
    while True:
        query = input(">>> ")
        if query == "exit":
            break
        response = llm.run(query)
        print(response)
