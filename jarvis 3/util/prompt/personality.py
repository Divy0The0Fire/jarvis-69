try:
    from modules.prompt.base import Prompt, Role, File
except ImportError:
    import sys
    import os
    sys.path.append(os.getcwd())
    from modules.prompt.base import Prompt, Role, File
# from rich import print
from rich import print
personalityJsonFile = r"data/personality/roster_jarvis.json"


prompt = Prompt(
    template=[
        File(personalityJsonFile)
    ]
)
print(prompt()[0])