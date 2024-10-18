try:
    from modules.llm.base import LLM, Model, ModelType, Role
except ImportError:
    import os
    import sys
    
    sys.path.append(os.path.dirname(__file__))
    from base import LLM, Model, ModelType, Role

from typing import Optional, List, Dict, Generator
from dotenv import load_dotenv
from rich import print
from copy import deepcopy
import os
import cohere



load_dotenv()

COMMAND_R = Model(name="command-r", typeof=ModelType.textonly)
COMMAND_R_PLUS = Model(name="command-r-plus", typeof=ModelType.textonly)

# TODO: Add more models here


class Cohere(LLM):
    def __init__(
        self,
        model: Model,
        apiKey: Optional[str] = None,
        messages: List[Dict[str, str]] = [],
        temperature: float = 0.3,
        systemPrompt: Optional[str] = None,
        maxTokens: int = 2048,
        cheatCode: Optional[str] = None,
        logFile: Optional[str] = None,
        extra: Dict[str, str] = {},
        ):
        super().__init__(model, apiKey, messages, temperature, systemPrompt, maxTokens, logFile)
        
        self.extra = extra
        self.cheatCode = cheatCode
        self.client: cohere.ClientV2 = self.constructClient()
        
        if cheatCode is None:
            p = self.testClient()
            if p:
                self.logger.info("Test successful for Cohere API key. Model found.")
        else:
            self.logger.info("Cheat code provided. Model found.")

    def constructClient(self):
        try:
            co = cohere.ClientV2(
                self.apiKey if self.apiKey is not None else os.environ["COHERE_API_KEY"]
            ) 
            return co
        except Exception as e:
            print(e)
            self.logger.error(e)

    def testClient(self):
        try:
            models = self.client.models.list().models
            for model in models:
                if model.name == self.model.name:
                    break
            else:
                self.logger.error("Model not found")
                raise Exception("Model not found in Cohere, please add it to the code.")
        except Exception as e:
            print(e)
            self.logger.error(e)
    
    def run(self, prompt: str, save: bool = True) -> str:
        toSend = []
        if save and prompt:
            self.addMessage(Role.user, prompt)
        elif not save and prompt:
            toSend.append(self.getMessage(Role.user, prompt))

        try:
            extra = {}
            if self.cheatCode is not None:
                extra["seed"] = 0
            
            chat_completion = self.client.chat(
                model = self.model.name,
                messages=self.messages + toSend,
                temperature=self.temperature,
                max_tokens=self.maxTokens,
                **extra,
                **self.extra
            )
        except Exception as e:
            self.logger.error(e)
            return "Please check log file some error occured."

        log_completion = deepcopy(chat_completion)
        self.logger.info(log_completion)
        
        if save:
            self.addMessage(Role.assistant, chat_completion.message.content[0].text)
        
        return chat_completion.message.content[0].text
        
        
    def streamRun(self, prompt: str, save: bool = True) -> Generator[str, None, None]:
        toSend = []
        if save and prompt:
            self.addMessage(Role.user, prompt)
        elif not save and prompt:
            toSend.append(self.getMessage(Role.user, prompt))

        try:
            extra = {}
            if self.cheatCode is not None:
                extra["seed"] = 0
            
            chat_completion = self.client.chat_stream(
                model = self.model.name,
                messages=self.messages + toSend,
                temperature=self.temperature,
                max_tokens=self.maxTokens,
                **extra,
                **self.extra
            )
        except Exception as e:
            self.logger.error(e)
            return "Please check log file some error occured."
        
        final_response = ""
        
        for completion in chat_completion:
            if completion.type == "message-end":
                self.logger.info(completion)
            elif completion.type == "content-delta":
                final_response += completion.delta.message.content.text
                yield completion.delta.message.content.text
        if save:
            self.addMessage(Role.assistant, final_response)
    
    
if __name__ == "__main__":
    from time import time as t
    llm = Cohere(COMMAND_R)
    # for i in llm.streamRun("what is 2+2?"):
    #     print(i)
    C =t()
    print(llm.run("whats elon musk networth"))
    print(t()-C)
