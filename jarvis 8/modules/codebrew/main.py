import os
import sys


print(os.path.dirname(__file__))

sys.path.append(os.path.dirname(__file__)+r"/../")

from llm.base import LLM, Role
from typing import Optional, Callable
from rich.console import Console
from rich.markdown import Markdown
from copy import deepcopy
import subprocess
import re
import io

console = Console()


class CodeBrew:
    def __init__(
            self,
            llm: LLM,  # Assuming LLM type is defined elsewhere
            maxRetries: int = 3,
            keepHistory: bool = True,
            globals: dict = {},
            input: Callable = input,
            print: Callable = print,
            verbose: bool = False
            ) -> None:
        self.llm = llm  # LLM instance
        self.maxRetries = maxRetries
        self.keepHistory = keepHistory
        self.verbose = verbose
        self.globals = globals

        self.globals['print'] = self.fakePrint

        self.input = input
        self.print = print
        
        self.tempString = ""

    def fakePrint(self, *args, **kwargs):
        string = io.StringIO()
        print(*args, **kwargs, file=string)
        val = string.getvalue()
        self.tempString += val

    def filterCode(self, txt: str) -> str:
        pattern = r"```python(.*?)```"
        matches: list[str] = re.findall(pattern, txt, re.DOTALL)
        for _match in matches:
            return _match.strip()

    def pipPackages(self, *packages: str):
        python_executable = sys.executable  # Automatically uses the current Python interpreter
        print(f"Installing {', '.join(packages)} with pip...")
        return subprocess.run(
            [python_executable, "-m", "pip", "install", *packages],
            capture_output=True,
            check=True,
        )

    def execute_script(self, script: str) -> tuple[str, str, int]:
        output, error = "", ""
        return_code = 0

        try:
            exec(script, self.globals)
            output = self.tempString
            self.tempString = ""
            print(f"{output = }")
        except Exception as e:
            error = str(e)
            print(e)
            return_code = 1

        return output, error, return_code

    def run(self, prompt: str) -> None:
        #TODO can be done better
        self.globals['input'] = self.input

        the_copy = self.llm.messages.copy()
        self.llm.addMessage(Role.user, prompt)
        _continue = True
        while _continue:
            _continue = False
            error, script, output, return_code = "", "", "", 0
            try:
                response = self.llm.run()
                self.llm.addMessage(Role.assistant, response)
                if self.verbose:
                    markdown = Markdown(response)
                    console.print(markdown)

                script = self.filterCode(response)
                if script:
                    output, error, return_code = self.execute_script(script)
            except KeyboardInterrupt:
                break
            if output:
                self.llm.addMessage(Role.user, f"LAST SCRIPT OUTPUT:\n{output}")

                if output.strip().endswith("CONTINUE"):
                    _continue = True
                else:
                    if self.verbose:
                        print("FINISHED ...")
                        markdown = Markdown(output)
                        console.print(markdown)
                    self.print(output.strip())
                    break
            else:
                if self.verbose:
                    markdown = Markdown(response)
                    console.print(markdown)
                self.print(response)

            if error:
                self.llm.addMessage(Role.user, f"Error: {error}")
            if return_code != 0:
                self.maxRetries -= 1
                if self.maxRetries > 0:
                    print("Retrying...\n")
                    self.print("let me try again.")
                    _continue = True

        if not self.keepHistory:
            self.llm.messages = the_copy


if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.dirname(__file__))
    sys.path.append(os.getcwd())
    
    from modules.llm._groq import LLAMA_32_90B_TEXT_PREVIEW, Groq, LLM
    from modules.codebrew.brew_prompt import codebrewPrompt, samplePrompt
    
    llm = Groq(LLAMA_32_90B_TEXT_PREVIEW, systemPrompt=codebrewPrompt(), messages=samplePrompt())
    
    codebrew = CodeBrew(llm, keepHistory=False, verbose=True)
    while True:
        codebrew.run(input(">>> "))
