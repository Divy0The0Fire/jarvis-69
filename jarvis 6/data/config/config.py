try:
    from modules.database.sq_dict import SQLiteDict
    from modules.database.text_store import TextStore
except ImportError:
    import os
    sys.path.append(os.getcwd())
    from modules.database.sq_dict import SQLiteDict
import sys

sqDictPath = r"data/sql/sq_dict.sql"
userNotebookPath = r"data/sql/user_notebook.sql"

sqDict = SQLiteDict(sqDictPath)

userNotebook = TextStore(userNotebookPath)



