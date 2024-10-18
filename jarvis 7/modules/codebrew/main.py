import os
import sys


print(os.path.dirname(__file__))

sys.path.append(os.path.dirname(__file__)+r"/../")

from llm.base import LLM, Role

import subprocess
import tempfile
import re

class CodeBrew:
    def __init__(
            self,
            llm: LLM,  # Assuming LLM type is defined elsewhere
            maxRetries: int = 3,
            keepHistory: bool = True,
            verbose: bool = False,
            ) -> None:
        self.llm = llm  # LLM instance
        self.maxRetries = maxRetries
        self.keepHistory = keepHistory
        self.verbose = verbose

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

    def _execute_script_in_subprocess(self, script: str) -> tuple[str, str, int]:
        output, error, return_code = "", "", 0
        try:
            python_executable = sys.executable  # Automatically uses the current Python interpreter
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_script:
                tmp_script_name = tmp_script.name
                tmp_script.write(script)
                tmp_script.flush()

                process = subprocess.Popen(
                    [python_executable, tmp_script_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL,  # Raises EOF error if subprocess asks for input
                    text=True,
                )
                while True:
                    _stdout = process.stdout.readline()
                    _stderr = process.stderr.readline()
                    if _stdout:
                        output += _stdout
                        print(_stdout, end="")
                    if _stderr:
                        error += _stderr
                        print(_stderr, end="", file=sys.stderr)
                    if _stdout == "" and _stderr == "" and process.poll() is not None:
                        break
                return_code = process.returncode
        except Exception as e:
            error += str(e)
            print(e)
            return_code = 1
        return output, error, return_code

    def execute_script(self, script: str) -> tuple[str, str, int]:
        return self._execute_script_in_subprocess(script)

    def run(self, prompt: str) -> None:
        the_copy = self.llm.messages.copy()
        self.llm.addMessage(Role.user, prompt)
        _continue = True
        while _continue:
            _continue = False
            error, script, output, return_code = "", "", "", 0
            try:
                response = self.llm.run()
                self.llm.addMessage(Role.assistant, response)
                script = self.filterCode(response)
                if script:
                    output, error, return_code = self.execute_script(script)
            except KeyboardInterrupt:
                break
            if output:
                self.llm.addMessage(Role.user, f"LAST SCRIPT OUTPUT:\n{output}")
                if output.strip().endswith("CONTINUE"):
                    _continue = True
            if error:
                self.llm.addMessage(Role.user, f"Error: {error}")
            if return_code != 0:
                self.maxRetries -= 1
                if self.maxRetries > 0:
                    print("Retrying...\n")
                    _continue = True
        if not self.keepHistory:
            self.llm.messages = the_copy
