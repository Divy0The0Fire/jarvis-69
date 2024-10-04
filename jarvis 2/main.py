# capture audio with microphone
# process audio [...]
# convert audio to text

# capture audio with microphone

# 

# from modules.sqlqueue import SqlQueue


# voicedata = SqlQueue("data/tmp/async_js_sr.queue.db")


# while True:
#     print(voicedata.get())


from modules.llm._togrther import Together, LLAMA_VISION_FREE, Role
from rich import print

llm = Together(LLAMA_VISION_FREE)


llm.addMessage(
    role=Role.user,
    content="my name is divyansh"
)

print(f"{llm.messages = }")

print(llm.run("what is my name?"))

print(f"{llm.messages = }")

