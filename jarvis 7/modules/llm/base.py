from abc import ABC, abstractmethod
from typing import Optional, Union, List, Dict, Any, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger

import logging
import os

load_dotenv()

class Role(Enum):
    system = "system"
    user = "user"
    assistant = "assistant"

class ModelType(Enum):
    textonly = "textonly"
    textandimage = "textandimage"


@dataclass
class Model:
    name: str
    typeof: ModelType


class LLM(ABC):
    def __init__(
        self,
        model: Model,
        apiKey: str,
        messages: List[Dict[str, str]] = [],
        temperature: float = 0.0,
        systemPrompt: Optional[str] = None,
        maxTokens: int = 2048,
        logFile: Optional[str] = None,
    ) -> None:
        
        self.apiKey = apiKey
        self.messages = messages
        self.temperature = temperature
        self.systemPrompt = systemPrompt
        self.maxTokens = maxTokens
        self.model = model

        # logger setup
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)  # Set default log level
        
        # Create a JSON formatter
        json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(name)s %(funcName)s')
        
        # Check if logFile is None, in that case use console logging (pseudo-logging)
        if logFile is None:
            # Pseudo-logging with RichHandler (for console output)
            from rich.logging import RichHandler
            rich_handler = RichHandler()
            self.logger.addHandler(rich_handler)
        else:
            # If logFile is provided, log to a file in JSON format
            LOG_FILE = logFile
            file_handler = logging.FileHandler(LOG_FILE)
            file_handler.setFormatter(json_formatter)
            self.logger.addHandler(file_handler)

        # Handle case where `model` is passed as a string
        if type(model) is str:
            self.logger.error("Model name must be a Model object. Fixed temporarily.")
            self.model = Model(model, ModelType.textandimage)
            model = self.model
        
        self.logger.info(
            {   
                "message": "Initializing LLM",
                "model": model.name,
                "modelType": model.typeof.value,
                "temperature": temperature
            }
        )

        # Set the appropriate message handler based on the model type
        self.addMessage = self.addMessageTextOnly if model.typeof == ModelType.textonly else self.addMessageVision
        
        if systemPrompt:
            self.addMessage(Role.system, systemPrompt)

        
    @abstractmethod
    def run(self, prompt: str, save: bool = True) -> str:
        raise NotImplementedError

    @abstractmethod
    def streamRun(self, prompt: str, save: bool = True) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def constructClient(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def testClient(self) -> None:
        raise NotImplementedError

    
    def addMessage(self, role: Role, content: str, imageUrl: Optional[str] = None) -> None:
        ...
    
    
    def addMessageVision(self, role: Role, content: str, imageUrl: Optional[str] = None) -> None:
        
        if imageUrl is None:
            return self.addMessageTextOnly(role, content, imageUrl)
        if type(role) is str:
            role = Role[role]

        message: Dict[str, list] = {"role": role.value, "content": []}

        if content:
            message["content"].append(
                {
                    "type": "text",
                    "text": content
                }
            )

        if imageUrl:
            message["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": imageUrl
                    }
                }
            )

        self.messages.append(message)

    def addMessageTextOnly(self, role: Role, content: str, imageUrl: Optional[str] = None) -> None:
        if type(role) is str:
            role = Role[role]

        if imageUrl is not None:
            self.logger.error("Image URL is not supported for text-only model. Ignoring the image URL.")
            
        self.messages.append({
            "role": role.value,
            "content": content
        })

    
    def getMessage(self, role: Role, content: str, imageUrl: Optional[str] = None) -> List[Dict[str, str]]:        
        if type(role) is str:
            role = Role[role]

        if imageUrl is not None:
            message: Dict[str, list] = {"role": role.value, "content": []}

            if content:
                message["content"].append(
                    {
                        "type": "text",
                        "text": content
                    }
                )

            if imageUrl:
                message["content"].append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": imageUrl
                        }
                    }
                )
            return message
        else:
            return {
                "role": role.value,
                "content": content
            }
        
    
    def log(self, **kwargs) -> None:
        self.logger.info(kwargs)


if __name__ == "__main__":
    print(Role.system.value)
