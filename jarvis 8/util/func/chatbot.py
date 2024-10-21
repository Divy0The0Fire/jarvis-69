import os, sys
import logging

sys.path.append(os.getcwd())

from datetime import datetime
from rich.logging import RichHandler
from modules.llm._groq import Groq, LLAMA_32_90B_TEXT_PREVIEW, LLM
from modules.prompt.base import Prompt, Role, File, Image, Text, Function
from textwrap import dedent
from typing import Optional
from util.func.emotion import listOfEmotion, Emotion
from util.func.user_notebook import UserNotebook
from rich import print

# Set up logging with both console and file handlers
def setup_logger(log_file: Optional[str]) -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Set default log level

    # Console logging using RichHandler
    rich_handler = RichHandler()
    logger.addHandler(rich_handler)

    # File logging
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

class Chatbot:
    def __init__(
        self,
        llm: LLM = Groq(LLAMA_32_90B_TEXT_PREVIEW, maxTokens=4096),
        systemPrompt: Optional[Prompt] = None,
        profile: Optional[str] = None,
        emotion: Optional[Emotion] = None,
        userNotebook: Optional[UserNotebook] = None,
        logFile: Optional[str] = None
    ) -> None:

        self.llm = llm
        self.profile = File(profile) if profile else Text("No profile provided")
        self.systemPrompt = systemPrompt

        if not systemPrompt:
            self.systemPrompt = Prompt(
                template=[
                    Function(
                        self.profilePrompt
                    ),
                    Function(
                        self.emotionPrompt,
                        emotion
                    ),
                    Function(
                        self.datetimePrompt
                    ),
                    Function(
                        self.userNotebookPrompt,
                        userNotebook
                    ),
                    Text("Please reply like normal human being generally in less words."),
                ],
                separator=f"\n{'-'*48}\n"
            )

        self.logger = setup_logger(logFile)  # Setup logger with the given log file
        self.emotion = emotion
        self.userNotebook = userNotebook
        self.logFile = logFile

        # Log initialization
        self.logger.info({
            "action": "Chatbot Initialization",
            "message": "Initializing Chatbot class",
            "emotion": bool(emotion),
            "userNotebook": bool(userNotebook),
            "logFile": logFile,
        })

        if self.emotion:
            self.logger.info({
                "action": "Chatbot Initialization",
                "message": "Emotion system initialized",
                "emotions_available": self.emotion.getEmotions(),
            })

        if self.userNotebook:
            self.logger.info(
                {
                    "action": "Chatbot Initialization",
                    "message": "User notebook initialized",
                    "notes_available": self.userNotebook
                }
            )


    def run(self, prompt: str, messages: Optional[list] = None) -> str:
        if not messages:
            messages = []
        
        self.llm.messages = [
            {
                "role": Role.system.value,
                "content": self.systemPrompt.prompt
            }
        ] + messages
        print(self.systemPrompt.prompt)
        self.logger.info({
            "action": "Chatbot Run",
            "message": "Running Chatbot",
            "prompt": hash(prompt)
        })
        return self.llm.run(prompt)


    def profilePrompt(self) -> str:
        return dedent(
            f"""\
            This is you profile:
            
            [| profile |]
            
            follow this profile instructions.\
            """
        ).replace("[| profile |]", self.profile.text)

    @staticmethod
    def emotionPrompt(emotion: Emotion) -> str:
        if not emotion:
            return ""
        return dedent(
            f"""\
            You are a language model that must express a specific emotion in your responses. Below is the emotion you need to embody:
            
            [| emotion list |]
            
            **Important**: You are required to respond only in this emotion. Your response must reflect the chosen emotion in every aspect, including tone, word choice, and overall expression. Any deviation from this emotion will not be acceptable.
            Your response should clearly reflect the specified emotion as described above.\
            """
        ).replace("[| emotion list |]", emotion.promptJson(indent=4))

    @staticmethod
    def userNotebookPrompt(userNotebook: UserNotebook) -> str:
        if not userNotebook:
            return ""
        return dedent(
            f"""\
            The user notebook contains the following records:
            
            [| userNotebook |]
            
            this contains all the records of the user.\
            """    
        ).replace("[| userNotebook |]", userNotebook.getText())

    @staticmethod
    def datetimePrompt() -> str:
        return dedent(
            f"""\
            **Date:** [| datetime |]\
            """
        ).replace("[| datetime |]", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

if __name__ == "__main__":
    # Example usage
    emotion = Emotion()  # Assuming Emotion is properly initialized
    userNotebook = UserNotebook()  # Assuming UserNotebook is properly initialized
    
    chatbot = Chatbot(emotion=emotion, userNotebook=userNotebook)
    while True:
        prompt = input("User: ")
        response = chatbot.run(prompt)
        print(f"Chatbot: {response}")

