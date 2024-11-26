try:
    from modules.llm.base import LLM, Model, ModelType, Role
except ImportError:
    import os
    import sys
    sys.path.append(os.path.dirname(__file__))
    from base import LLM, Model, ModelType, Role

import google.generativeai as genai
from google.generativeai.types import File
from google.generativeai import GenerationConfig, list_models

from typing import Optional, List, Dict
from dotenv import load_dotenv
from rich import print
import base64
import requests
import PIL.Image
from io import BytesIO


load_dotenv()

GEMINI_1_5_FLASH_002 = Model(name="gemini-1.5-flash-002", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH_8B_EXP_0924 = Model(name="gemini-1.5-flash-8b-exp-0924", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH_8B_LATEST = Model(name="gemini-1.5-flash-8b-latest", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH_8B_001 = Model(name="gemini-1.5-flash-8b-001", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH_8B = Model(name="gemini-1.5-flash-8b", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH_8B_EXP_0827 = Model(name="gemini-1.5-flash-8b-exp-0827", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH_001 = Model(name="gemini-1.5-flash-001", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH = Model(name="gemini-1.5-flash", typeof=ModelType.textandfile)


GEMINI_1_0_PRO_LATEST = Model(name="gemini-1.0-pro-latest", typeof=ModelType.textandimage)
GEMINI_1_0_PRO = Model(name="gemini-1.0-pro", typeof=ModelType.textandimage)
GEMINI_PRO = Model(name="gemini-pro", typeof=ModelType.textandimage)
GEMINI_1_0_PRO_001 = Model(name="gemini-1.0-pro-001", typeof=ModelType.textandimage)
GEMINI_1_0_PRO_VISION_LATEST = Model(name="gemini-1.0-pro-vision-latest", typeof=ModelType.textandimage)
GEMINI_PRO_VISION = Model(name="gemini-pro-vision", typeof=ModelType.textandimage)
GEMINI_1_5_PRO_LATEST = Model(name="gemini-1.5-pro-latest", typeof=ModelType.textandimage)
GEMINI_1_5_PRO_001 = Model(name="gemini-1.5-pro-001", typeof=ModelType.textandimage)
GEMINI_1_5_PRO_002 = Model(name="gemini-1.5-pro-002", typeof=ModelType.textandimage)
GEMINI_1_5_PRO = Model(name="gemini-1.5-pro", typeof=ModelType.textandimage)


def getImageByUrl(url: str) -> PIL.Image.Image:
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes
        return PIL.Image.open(BytesIO(response.content))
    except Exception as e:
        raise ValueError(f"Failed to load image from URL: {str(e)}")


def getImageByBase64(imageBase64: str) -> PIL.Image.Image:
    if imageBase64.startswith("data:image/"):
        imageBase64 = imageBase64.split(",")[1]
    return PIL.Image.open(BytesIO(base64.b64decode(imageBase64)))


def getImageByFile(file: str) -> PIL.Image.Image:
    return PIL.Image.open(file)

def getImage(any: str | PIL.Image.Image | bytes) -> PIL.Image.Image:
    def checkIfUrl(any: str) -> bool:
        return any.startswith("http")
    if checkIfUrl(any):
        return getImageByUrl(any)
    elif isinstance(any, str):
        return getImageByBase64(any)
    elif isinstance(any, bytes):
        return getImageByFile(any)
    else:
        raise ValueError("Invalid image type")

def convert_openai_to_gemini(openai_messages: list) -> list:
    """
    Convert OpenAI message format to Gemini message format.
    
    Args:
        openai_messages (list): Messages in OpenAI format
        
    Returns:
        list: Messages in Gemini format with balanced user/model interactions
    """

    # Initial conversion to Gemini format
    gemini_messages = []
    system_messages = []

    # Convert messages to Gemini format
    for message in openai_messages:
        role = message["role"]
        content = message["content"]

        if role == "system":
            system_messages.append(content)
        elif role == "user":
            if isinstance(content, list):
                for content_item in content:
                    if content_item["type"] == "text":
                        gemini_messages.append({
                            "role": "user",
                            "parts": [content_item["text"]]
                        })
                    elif content_item["type"] == "image_url":
                        gemini_messages.append({
                            "role": "user",
                            "parts": [getImage(content_item["image_url"]["url"])]
                        })
            else:
                gemini_messages.append({
                    "role": "user",
                    "parts": [content]
                })
        elif role == "assistant":
            gemini_messages.append({
                "role": "model",
                "parts": [content]
            })

    # Combine consecutive messages from the same role
    consolidated_messages = []
    previous_role = None

    for message in gemini_messages:
        current_role = message["role"]
        if current_role == previous_role:
            consolidated_messages[-1]["parts"].append(message["parts"][0])
        else:
            consolidated_messages.append(message)
            previous_role = current_role

    # Balance user/model interactions by inserting empty messages
    balanced_messages = []
    previous_role = None

    for message in consolidated_messages:
        current_role = message["role"]
        if current_role == previous_role == "user":
            balanced_messages.append({
                "role": "model",
                "parts": ["\n"]
            })
            previous_role = "model"
        elif current_role == previous_role == "model":
            balanced_messages.append({
                "role": "user",
                "parts": ["\n"]
            })
            previous_role = "user"
        
        balanced_messages.append(message)
        previous_role = current_role

    return balanced_messages


class Gemini(LLM):
    def __init__(
        self,
        model: Model,
        apiKey: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        temperature: float = 1.0,
        systemPrompt: Optional[str] = None,
        maxTokens: int = 2048,
        cheatCode: Optional[str] = None,
        logFile: Optional[str] = None,
        extra: Dict[str, str] = {}
    ):
        messages = messages if messages is not None else []
        super().__init__(model, apiKey, messages, temperature, systemPrompt, maxTokens, logFile)
        
        self.extra = extra
        self.cheatCode = cheatCode
        self.files: List[File] = []
        
        # Create the model
        self.generation_config = GenerationConfig(
            temperature=temperature,
            top_p=0.95,
            top_k=40,
            max_output_tokens=maxTokens,
            response_mime_type="text/plain",
        )
        self.client: genai.GenerativeModel = self.constructClient()
        genai.configure(api_key=apiKey if apiKey is not None else os.environ["GEMINI_API_KEY"])
        if cheatCode is None:
            p = self.testClient()
            if p:
                self.logger.info("Test successful for Gemini API key. Model found.")
        else:
            self.logger.info("Cheat code provided. Model found.")

    def constructClient(self):
        try:
            return genai.GenerativeModel(
                model_name=self.model.name,
                generation_config=self.generation_config,
                system_instruction=self.systemPrompt,
            )
        except Exception as e:
            print(e)
            self.logger.error(e)

    def testClient(self):
        try:
            models: List[str] = [i.name.removeprefix("models/") for i in list_models()]
            if self.model.name not in models:
                raise Exception(f"Model {self.model.name} not found!")
            return True
        except Exception as e:
            print(e)
            self.logger.error(e)
    
    def run(self, prompt: str = "", imageUrl: Optional[str] = None, save: bool = True) -> str:
        toSend = []
        if save and prompt:
            self.addMessage(Role.user, prompt, imageUrl)
        elif not save and prompt:
            toSend.append(self.getMessage(Role.user, prompt, imageUrl))
        try:
            chat = self.client.start_chat(
                history=convert_openai_to_gemini(self.messages + toSend)
        )
            response = chat.send_message("\n", **self.extra)
        except Exception as e:
            print(e)
            self.logger.error(e)
            return "Please check log file some error occured."
        self.logger.info(response)
        
        if save:
            self.addMessage(Role.assistant, response.text)
        return response.text

    def streamRun(self, prompt: str = "", imageUrl: Optional[str] = None, save: bool = True):
        toSend = []
        if save and prompt:
            self.addMessage(Role.user, prompt, imageUrl)
        elif not save and prompt:
            toSend.append(self.getMessage(Role.user, prompt, imageUrl))
        try:
            chat = self.client.start_chat(
                history=convert_openai_to_gemini(self.messages + toSend)
            )
            response = chat.send_message("\n", stream=True, **self.extra)
        except Exception as e:
            print(e)
            self.logger.error(e)
            return "Please check log file some error occured."
        try:
            final_response = ""
            for chunk in response:
                final_response += chunk.text
                yield chunk.text
            if save:
                self.addMessage(Role.assistant, final_response)
            return final_response
        except Exception as e:
            print(e)
            self.logger.error(e)
            return "Please check log file some error occured."

if __name__ == "__main__":
    gemini = Gemini(GEMINI_1_5_FLASH_002)
    # Use a direct image URL instead of a search page
    image_url = "https://i.pinimg.com/236x/5e/9a/05/5e9a0599b298390425310ac88c91760f.jpg"
    print(*gemini.streamRun("what is in the image?", imageUrl=image_url))
