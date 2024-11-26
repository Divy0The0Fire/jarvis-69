import sqlite3
import threading
from rich import print
from typing import List, Optional, Tuple

class TextStore:
    def __init__(self, dbName: str) -> None:
        self.dbName = dbName
        self.connection = sqlite3.connect(self.dbName, check_same_thread=False)
        self.lock = threading.Lock()  # Initialize a lock
        self.createTable()
    
    def createTable(self) -> None:
        with self.lock:  # Acquire the lock
            with self.connection:
                self.connection.execute(''' 
                    CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        textLine TEXT NOT NULL,
                        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        lastModified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        lastViewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

    def addRecord(self, textLine: str) -> None:
        with self.lock:  # Acquire the lock
            with self.connection:
                self.connection.execute(''' 
                    INSERT INTO records (textLine, created, lastModified, lastViewed)
                    VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (textLine,))

    def updateRecord(self, recordId: int, newTextLine: str) -> None:
        with self.lock:  # Acquire the lock
            with self.connection:
                self.connection.execute(''' 
                    UPDATE records
                    SET textLine = ?, lastModified = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (newTextLine, recordId))

    def deleteRecord(self, recordId: int) -> None:
        with self.lock:  # Acquire the lock
            with self.connection:
                self.connection.execute(''' 
                    DELETE FROM records WHERE id = ?
                ''', (recordId,))

    def getRecord(self, recordId: int) -> Optional[Tuple[int, str, str, str, str]]:
        with self.lock:  # Acquire the lock
            with self.connection:
                result = self.connection.execute(''' 
                    SELECT * FROM records WHERE id = ?
                ''', (recordId,)).fetchone()
                
                if result:
                    # Update lastViewed timestamp
                    self.connection.execute(''' 
                        UPDATE records
                        SET lastViewed = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (recordId,))
                    
                return result

    def listRecords(self) -> List[Tuple[int, str, str, str, str]]:
        with self.lock:  # Acquire the lock
            with self.connection:
                return self.connection.execute(''' 
                    SELECT * FROM records
                ''').fetchall()

    def getFirstNRecords(self, n: int) -> List[Tuple[int, str, str, str, str]]:
        with self.lock:  # Acquire the lock
            with self.connection:
                return self.connection.execute(''' 
                    SELECT * FROM records
                    ORDER BY id ASC
                    LIMIT ?
                ''', (n,)).fetchall()

    def getLastNRecords(self, n: int) -> List[Tuple[int, str, str, str, str]]:
        with self.lock:  # Acquire the lock
            with self.connection:
                return self.connection.execute(''' 
                    SELECT * FROM records
                    ORDER BY id DESC
                    LIMIT ?
                ''', (n,)).fetchall()[::-1]  # Reverse order to get it in correct sequence

    def getRecordsSlice(self, start: int, end: int) -> List[Tuple[int, str, str, str, str]]:
        with self.lock:  # Acquire the lock
            with self.connection:
                return self.connection.execute(''' 
                    SELECT * FROM records
                    WHERE id >= ? AND id < ?
                    ORDER BY id ASC
                ''', (start, end)).fetchall()
    
    def getText(self, start: Optional[int] = None, end: Optional[int] = None) -> str:
        if start is None and end is None:
            data = self.listRecords()
            text = []
            for d in data:
                text.append(f"{d[0]}. {d[1]}\n")
            return "".join(text).removesuffix("\n")
        else:
            data = self.getRecordsSlice(start, end)
            text = []
            for d in data:
                text.append(f"{d[0]}. {d[1]}\n")
            return "".join(text).removesuffix("\n")
    
    @property
    def text(self) -> str:
        return self.getText()
    
    def __del__(self) -> None:
        self.connection.close()

if __name__ == "__main__":
    
    # Usage example
    
    db = TextStore("my_text_db.sql")

    # # Adding new records
    db.addRecord("First line of text.")
    db.addRecord("Second line of text.")
    db.addRecord("Third line of text.")
    db.addRecord("Fourth line of text.")
    db.addRecord("Fifth line of text.")
    print(db.text)

    # Uncomment and test other functionalities as needed.
