import types
from dataclasses import dataclass, field
from textwrap import dedent
import os, sys


sys.path.append(os.getcwd())

from modules.llm._groq import Groq, Model, ModelType, Role


x3b = Model(name="llama-3.2-11b-text-preview", typeof=ModelType.textonly)


@dataclass
class Fn:
    name: str
    discription: str
    kwargs: dict[str, types.GenericAlias] = field(default_factory=dict)
    
    def __post_init__(self):
        # Ensure only one parameter is in kwargs
        assert len(self.kwargs) == 1, "Only one param is allowed. Not more than one. Not less than one."
        self.cache = False
    
    def prompt(self):
        # Generate the prompt string based on the provided parameters
        if self.cache:
            return self.cache

        kwarg = list(self.kwargs.items())
        param_key, param_type = kwarg[0]

        self.cache = dedent(f"""
        {{
            "function_name": "{self.name}",
            "description": "{self.discription}",
            "kwargs": {{"{param_key}": "{param_type}"}}
        }}
        """).strip()

        return self.cache




systemPromptText = """\
You are an exact and strict Decision-Making Model tasked solely with classifying the type of query presented to you.

***Your responsibilities:***
- **Do not** perform the requested tasks.
- **Do not** respond to any query directly.
- **Do ASK** follow up questions if necessary. by returning followUp 'function_name question and kwarg q: str. the call a function like this:'

{fn_prompts}

***If the query involves performing multiple tasks can multiple functions***
- Parse the query.
- Use Python's `eval` to evaluate the parameter, ensuring it matches the expected data type.
"""

exampleSystemPromptText = """\

you can call functions like (json) this:

[
    {
        "name": "function_name",
        "kwargs": {
            "arg1": 1,
            "st": 'hello'
        }
    },
    ...
]

"""




fun = [
    Fn(
        name="general",
        discription="if the query can be answerend by a llm. based chatbot",
        kwargs={
        "query": str
        }
    ),

    Fn(
        name="realtime",
        discription="if the query is asking for up-to-date information or information that can change anytime.",
        kwargs={
            "query": str
        }
    ),

    Fn(
        name="play",
        discription="if the query is asking to play any song like 'play afsanay by ys', 'play let her go', etc.",
        kwargs={
            "song_name": str
        }
    ),

    Fn(
        name="generate image",
        discription="if the query is asking to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc.",
        kwargs={
            "image_prompt": str
        }
    ),

    Fn(
        name="system",
        discription="if the query is asking to mute, unmute, volume up, volume down, any win64 task.",
        kwargs={
            "task_name": str
        }
    ),

    Fn(
        name="content",
        discription="if the query is asking to write code or any other content call it",
        kwargs={
            "topic": str
        }
    )
]


fn_prompts = "\n,".join([fn.prompt() for fn in fun])


systemPromptText = systemPromptText.format(fn_prompts=fn_prompts)
systemPromptText += exampleSystemPromptText

print(systemPromptText)

llm = Groq(
    model=x3b,
    systemPrompt=systemPromptText,
    cheatCode="1",
    extra={"response_format": {"type": "json_object"}}
    )

# while True:
#     i = input(">>> ")
#     print(llm.run(i))

