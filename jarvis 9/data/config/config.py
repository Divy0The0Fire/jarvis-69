import os, sys
sys.path.append(os.getcwd())
from modules.database.sq_dict import SQLiteDict
from modules.database.text_store import TextStore
from modules.llm.base import ModelType
from modules.prompt.base import Prompt, Role, Text, File, Function

from modules.codebrew import codebrewPrompt, samplePrompt, CodeBrew
from modules.database.chat_history import ChatHistoryDB

# ------------------------------------------------ #
from modules.llm._cohere import Cohere, COMMAND_R_PLUS
from modules.llm._groq import Groq, LLAMA_32_90B_VISION_PREVIEW, LLAMA_32_90B_TEXT_PREVIEW
# ------------------------------------------------ #

# CHEAT CODE
cheatCode = os.getenv("CHEAT_CODE")

# SCREENSHOT
SCREENSHOT = os.getenv("SCREENSHOT", "False").lower() == "true"

# Jarvis SQL
sqDictPath = rf"{os.getenv('DATA_DIR')}\sql\sq_dict.sql"
userNotebookPath = rf"{os.getenv('DATA_DIR')}\sql\user_notebook.sql"

sqDict = SQLiteDict(sqDictPath)

userNotebook = TextStore(userNotebookPath)

# Jarvis profile found in data/personality/
profile = rf"{os.getenv('DATA_DIR')}\personality\humor_jarvis.json"

# Jarvis DMM LLMs
dmmLLM = Cohere(COMMAND_R_PLUS, maxTokens=4096, logFile=os.getenv("DATA_DIR") + r"/log/dmm.log", cheatCode=cheatCode)
edmmLLM = Groq(LLAMA_32_90B_TEXT_PREVIEW, maxTokens=4096, logFile=os.getenv("DATA_DIR") + r"/log/eddm.log", cheatCode=cheatCode)
ndmmLLM = Groq(LLAMA_32_90B_TEXT_PREVIEW, maxTokens=4096, logFile=os.getenv("DATA_DIR") + r"/log/nddm.log", cheatCode=cheatCode)

# CodeBrew LLM prompt template
codeBrewPromptTemplate = Prompt(
    role=Role.system,
    template=[
        Function(codebrewPrompt),
        Text("\n\nHere are some example interactions:"),
        Function(samplePrompt)
    ],
    separator="\n\n"
)

# Update the codeBrewLLM initialization
codeBrewLLM = Groq(
    LLAMA_32_90B_TEXT_PREVIEW, 
    maxTokens=4096, 
    systemPrompt=codeBrewPromptTemplate(),
    logFile=os.getenv("DATA_DIR") + r"/log/codebrew.log", 
    cheatCode=cheatCode
)

codeBrew = CodeBrew(codeBrewLLM, keepHistory=False, verbose=True)


chatBotLLM = Groq(LLAMA_32_90B_VISION_PREVIEW, maxTokens=4096, logFile=os.getenv("DATA_DIR") + r"/log/chatbot.log", cheatCode=cheatCode)


historyDb = ChatHistoryDB(rf"{os.getenv('DATA_DIR')}\sql\chat_history.sql")

dmmHistoryDb = ChatHistoryDB(rf"{os.getenv('DATA_DIR')}\sql\dmm.sql")
edmmHistoryDb = ChatHistoryDB(rf"{os.getenv('DATA_DIR')}\sql\edmm.sql")
ndmmHistoryDb = ChatHistoryDB(rf"{os.getenv('DATA_DIR')}\sql\ndmm.sql")
