"Emotion Decision Making Model"
import os, sys
sys.path.append(os.getcwd())

from modules.llm._groq import Groq, LLAMA_32_90B_TEXT_PREVIEW
from modules.llm_fn_call.blueprint.one_param import Fn, generateSystemPrompt
from modules.prompt.base import Prompt, Role, File, Image, Text, Function
from util.func.emotion import Emotion, listOfEmotion, sqDict
from rich import print

functions = [
    Fn(
        name="addEmotion",
        description=f"Add that emotion to current system tray. the new_emotion can be any emotion in the possible list of emotion {listOfEmotion}",
        parameter={"new_emotion": "string"}
    ),
    Fn(
        name="removeEmotion",
        description=f"Remove that emotion from current system tray. the remove_emotion can be any emotion in the possible list of emotion {listOfEmotion}",
        parameter={"remove_emotion": "string"}
    )
]


def currentEmotions() -> list[str]:
    return f"the current system tray emotions are list({sqDict.get('emotion', [])})"


systemPromptTemplate = Prompt(
    template=[
        Function(
            currentEmotions
        ),
        Function(
            generateSystemPrompt,
            functions
        ),
        Text(
            "you have to choose the emotions that chatbot will know to responce the user decide this on the basis of users chat history."
        )
    ],
    separator=f"\n{'-'*48}\n"
)

if __name__ == "__main__":
    from time import time as t
    
    llm = Groq(LLAMA_32_90B_TEXT_PREVIEW, systemPrompt=systemPromptTemplate.prompt)
    while 1:
        q = input(">>> ")
        start = t()
        print(llm.run(q, save=False))
        print(t() - start)
