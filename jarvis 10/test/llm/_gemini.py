import os
import google.generativeai as genai
from google.generativeai.types import File
from google.generativeai import GenerationConfig, list_models
from rich import print

genai.configure(api_key="AIzaSyCbZXbWM6ThBXqXpJCwkVTY1w09s2etq-Q")

print([i.name for i in list_models()])


def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file


# # Create the model
# generation_config = {
#   "temperature": 1,
#   "top_p": 0.95,
#   "top_k": 40,
#   "max_output_tokens": 8192,
#   "response_mime_type": "text/plain",
# }

generation_config = GenerationConfig(
    temperature=1,
    top_p=0.95,
    top_k=40,
    max_output_tokens=8192,
    response_mime_type="text/plain",
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="dfQWFRQFQfqFQqFFQfqFFQfqQf",
)

# TODO Make these files available on the local file system
# You may need to update the file paths
from time import time as t

C = t()
files = [
    upload_to_gemini("image.png", mime_type="image/png"),
]
files[0].sha256_hash
print(f"Time taken: {t() - C} Files: {files}")
print(type(files[0]))
print(files[0])
print(type(File))
print(File)

from time import time as t

st = t()
chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                "Hello\n",
            ],
        },
        {
            "role": "model",
            "parts": [
                "Hello there! How can I help you today?\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "Hello\n",
                "hello\n",
            ],
        },
        {
            "role": "model",
            "parts": [
                "Hello!  Is there anything I can assist you with?\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                " ",
            ],
        },
        {
            "role": "model",
            "parts": [
                "Okay, I'm ready when you are.  Please let me know what you need.\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                " ",
            ],
        },
        {
            "role": "model",
            "parts": [
                "I understand.  Is there something specific you'd like to talk about, or a task you'd like me to perform?  I'm here to help!\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                " ",
            ],
        },
        {
            "role": "model",
            "parts": [
                "I'm still here and ready to assist you.  Please let me know what",
            ],
        },
        # {
        #   "role": "user",
        #   "parts": [
        #     files[0],
        #   ],
        # },
        # {
        #   "role": "model",
        #   "parts": [
        #     "That's a screenshot of our previous conversation.  The OCR has captured the two questions I asked you:\n\n1. \"can assist you with?\" (there's a typo; it should be \"can I assist you with?\")\n2. \"u are. Please let me know what you need.\" (this is also a typo; it should be \"I am ready when you are. Please let me know what you need.\")\n\nIs there anything you need help with now?\n",
        #   ],
        # },
    ]
)
openai = [
    {
      "role": "user", 
      "content": "Hello, how are you?"
    },
    {
      "role": "assistant", 
      "content": "I'm doing well, thank you!"
    },
    {
      "role": "user", 
      "content": [
        {
          "type": "text", 
          "text": "Hello, how are you?"
        },
        {
          "type": "image_url", 
          "image_url": {"url": "https://example.com/image.png"}
        },
      ]},
]
print(f"Time taken: {t() - st}")

response = chat_session.send_message("pick random number between 1 and 10")
from rich import print
print(response)
