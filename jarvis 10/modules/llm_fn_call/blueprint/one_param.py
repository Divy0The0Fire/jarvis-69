import types
import os, sys
from dataclasses import dataclass, field
from textwrap import dedent

sys.path.append(os.getcwd())

@dataclass
class Fn:
    name: str
    description: str
    parameter: dict[str, types.GenericAlias] = field(default_factory=dict)

    def __post_init__(self):
        # Ensure only one parameter is in kwargs
        assert len(self.parameter) == 1, "Only one param is allowed. Not more than one. Not less than one."
        self.cache = False
    
    @property
    def prompt(self):
        # Generate the prompt string based on the provided parameters
        if self.cache:
            return self.cache

        kwarg = list(self.parameter.items())
        param_key, param_type = kwarg[0]
        
        self.cache = dedent(f"""
            -> Respond with {self.name}({param_key}="yourvalue")
            {self.description}
            . The {param_key} type is {param_type}.
            """).strip()

        return self.cache


systemPromptTemplate = """\
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
*** Do not answer any query, just decide what kind of query is given to you. ***

[| {functions} |]

***If the query involves performing multiple tasks do it. just saprate them with commas. you can call 1 task many times***
"""


def generateSystemPrompt(functions: list[Fn]) -> str:
    """Generate a formatted prompt for the LLM."""
    fn_prompts = "\n".join([f.prompt for f in functions])
    return systemPromptTemplate.replace("[| {functions} |]", fn_prompts)

if __name__ == "__main__":
    fun = [
        Fn(
            name="general",
            description="if the query can be answerend by a llm. based chatbot",
            parameter={
            "query": str|None
            }
        ),

        Fn(
            name="realtime",
            description="if the query is asking for up-to-date information or information that can change anytime.",
            parameter={
                "query": str
            }
        ),

        Fn(
            name="play",
            description="if the query is asking to play any song like 'play afsanay by ys', 'play let her go', etc.",
            parameter={
                "song_name": str
            }
        ),

        Fn(
            name="generate image",
            description="if the query is asking to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc.",
            parameter={
                "image_prompt": str
            }
        ),

        Fn(
            name="system",
            description="if the query is asking to mute, unmute, volume up, volume down, any win64 task.",
            parameter={
                "task_name": str
            }
        ),

        Fn(
            name="content",
            description="if the query is asking to write code or any other content call it",
            parameter={
                "topic": str
            }
        )
    ]


    fn_prompts = "\n".join([fn.prompt for fn in fun])

    print(systemPromptTemplate.format(functions=fn_prompts))
    from modules.llm._cohere import Cohere, COMMAND_R

    llm = Cohere(
        model=COMMAND_R,
        systemPrompt=systemPromptTemplate.format(functions=fn_prompts),
        cheatCode="1"
        )

    while True:
        i = input(">>> ")
        print(llm.run(i))
