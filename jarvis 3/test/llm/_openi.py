from openai import OpenAI
from rich import print

from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {
      "role": "user",
      "content": "hello"
        
    },

  ],
  temperature=1,
  max_tokens=2048,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0,
)
print(response)