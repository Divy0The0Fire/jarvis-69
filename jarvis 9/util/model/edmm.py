"Emotion Decision Making Model"
import os, sys
sys.path.append(os.getcwd())

from modules.llm._groq import Groq, LLAMA_32_90B_TEXT_PREVIEW
from modules.llm_fn_call.blueprint.one_param import Fn, generateSystemPrompt
from modules.prompt.base import Prompt, Role, File, Image, Text, Function
from util.func.emotion import listOfEmotion, sqDict
from rich import print
from textwrap import dedent

functions = [
    Fn(
        name="addEmotion",
        description=f"Add an emotion to the current system tray to reflect the chatbot's emotional state. Choose from: {', '.join(listOfEmotion)}. Use this when the conversation or context suggests a new emotional response is appropriate.",
        parameter={"new_emotion": "string"}
    ),
    Fn(
        name="removeEmotion",
        description=f"Remove an emotion from the current system tray when it's no longer relevant. Choose from: {', '.join(listOfEmotion)}. Use this when the conversation shifts away from a particular emotional context.",
        parameter={"remove_emotion": "string"}
    ),
    Fn(
        name="doPass",
        description="Use this when the current query doesn't require any changes to the emotional state.",
        parameter={"isPass": "bool"}
    )
]


def currentEmotions() -> list[str]:
    return f"the current system tray emotions are list({sqDict.get('emotion', [])})"


systemPromptTemplate = Prompt(
    template=[
        Function(
            generateSystemPrompt,
            functions
        ),
        Text(
            dedent(
            f"""
            Manage the chatbot's emotional state based on the conversation context and user's input.
            Available emotions: {', '.join(listOfEmotion)}

            Guidelines for managing emotions:
            1. Add emotions when:
               - The user expresses strong feelings
               - The topic of conversation changes significantly
               - There's a need to empathize with the user
            2. Remove emotions when:
               - The conversation moves to a neutral topic
               - The intensity of an emotion decreases
               - A conflicting emotion becomes more relevant
            3. Maintain a balanced emotional state:
               - Limit the number of active emotions to 2-3 at a time
               - Ensure the emotional state aligns with the conversation context
            4. Consider the intensity and appropriateness of emotions:
               - Use stronger emotions sparingly and in response to significant events
               - Prefer milder emotions for everyday conversations
            5. Transition smoothly between emotions:
               - Gradually introduce new emotions and phase out old ones
               - Avoid abrupt emotional changes unless the situation warrants it

            Always aim for a natural, appropriate, and empathetic emotional response.
            """
            )
        ),
        Function(
            currentEmotions
        ),
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
    print(systemPromptTemplate.prompt)
