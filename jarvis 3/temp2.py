from modules.prompt.base import Prompt, Role, File, Image, Text, Function
from modules.llm._groq import Groq, LLAMA_31_70B_VERSATILE


from datetime import datetime



# llm = Groq(
#     model=LLAMA_31_70B_VERSATILE,
#     systemPrompt=f"current time is {datetime.now() = }",
#     )

# resp = llm.run("what is time current time.")
# print(resp)

def getTime(a):
    print(a)
    return f"The current time is {datetime.now()}"

prompt = Prompt(
    template=[
        "hello",
        File("personaldetails.txt"),
        Function(getTime, 21),
        Image("camera input", "http://www.cam.com"),
        {
            "role": Role.assistant
        }
    ],
    separator=f'\n{"-"*50}\n'
)

print(prompt.promptOnly)





