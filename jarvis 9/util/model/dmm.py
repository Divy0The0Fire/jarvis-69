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
            Use this function to seek clarification when the user's instructions are unclear or incomplete.
            Ask follow-up questions in a casual, conversational manner. Examples:
            - "By the way, did you mean...?"
            - "Do you want me to...?"
            - "Should I...?"
            - "Can you tell me more about...?"
            Only use this when absolutely necessary to understand the user's intent.
            """
        ),
        parameter={"query": "string"}
    ),
    Fn(
        name="chatbot",
        description=dedent(
            """
            Use this function for general queries or real-time information requests.
            The chatbot has access to:
            1. Internet for current information
            2. User's interaction history
            3. User's camera
            4. Screenshot capabilities
            Ideal for questions about current events, general knowledge, or referencing past interactions.
            """
        ),
        parameter={"prompt": "string"}
    ),
    Fn(
        name="url",
        description=dedent(
            """
            Call this function ONLY when the user explicitly requests to open a specific URL.
            Ensure you have clear confirmation of the user's intent before using this function.
            Provide the exact URL as the input parameter.
            """
        ),
        parameter={"url": "string"}
    ),
    Fn(
        name="pythonDon",
        description=dedent(
            """
            Use this function for tasks requiring Python code execution or automation.
            'pythonDon' is an advanced AI that can:
            - Generate and run Python code
            - Process data and manipulate files
            - Perform system-level operations (with admin access)
            - Control software and hardware (e.g., play songs, open applications)
            - Retrieve system information (e.g., IP address, PC details)
            Pass only the task description or problem statement. DO NOT include Python code in your query.  
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
