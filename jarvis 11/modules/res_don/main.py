import os
import sys

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.getcwd())

from nara.llm._openai import OpenAI, GPT4OMINI
from filebrew.main import filebrewPrompt, samplePrompt, FileBrew
sys.path.append(os.getcwd()+"/tools/")
from tools.textfile import TextFile

llm = OpenAI(GPT4OMINI, apiKey="", systemPrompt=filebrewPrompt(), messages=samplePrompt())

codebrew = FileBrew(llm, keepHistory=True, verbose=True)


prompt = """
file - path is example\sample.txt
task - tell me everything about this oggy using this files and save all the key points in text file name oggy.txt.
PLEASE FIRST READ THE FILE THEN CONTINUE AND ONLY AFTER YOU HAVE READ THE FILE ANSWER THE QUESTION AND SAVE IT. YOU CAN TAKE 8 ITERATIONS TO ANSWER THE QUESTION.
"""

codebrew.run(prompt)
while True:
    codebrew.run(input(">>> "))