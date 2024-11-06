"Notebook Decision Making Model"
import os, sys
sys.path.append(os.getcwd())


from modules.llm._groq import Groq, LLAMA_32_90B_TEXT_PREVIEW
from modules.llm_fn_call.blueprint.one_param import Fn, generateSystemPrompt
from modules.prompt.base import Prompt, Role, File, Image, Text, Function
from data.config.config import userNotebook

from rich import print


functions = [
    Fn(
        name="addRecord",
        description="Adds a new text entry to the notebook",
        parameter={"textLine": "string"}
    ),
    Fn(
        name="deleteRecord",
        description="Deletes an existing record from the notebook by record ID",
        parameter={"recordId": "integer"}
    ),
    Fn(
        name="updateRecord",
        description="Updates an existing record in the notebook pass the record ID and the new text line",
        parameter={"record": "dict[integer, string]"}
    ),
    Fn(
        name="doPass",
        description="when you don't think its import to store just pass it.",
        parameter={"isPass": "bool"}
    )
]

def currentUserNotebook() -> str:
    return f"""current userNotebook text (recordId, textLine):\n```\n{userNotebook.text}\n```"""

systemPromptTemplate = Prompt(
    template=[
        Function(
            currentUserNotebook
        ),
        Function(
            generateSystemPrompt,
            functions
        ),
        Text(
            "you have to store all the users personal history for chatbot. save all the things that you think are import or can be asked by chatbot. users favorite food, favourite color, favourite movie, people's name, role, any instruction, all the things. it is important to store it."
        )
    ],
    separator=f"\n{'-'*48}\n"
)


if __name__ == "__main__":
    llm = Groq(LLAMA_32_90B_TEXT_PREVIEW, systemPrompt=systemPromptTemplate.prompt)
    while True:
        query = input(">>> ")
        if query == "exit":
            break
        response = llm.run(query)
        print(response)