import sqlite3
from typing import List, Dict, Optional
import threading

class ChatHistoryDB:
    def __init__(self, dbName: str):
        self.dbName = dbName
        self.connection = sqlite3.connect(self.dbName, check_same_thread=False)
        self.lock = threading.Lock()  # Create a lock object
        self.createTable()
        
    def createTable(self):
        with self.lock:  # Ensure thread-safe access
            with self.connection:
                self.connection.execute('''
                    CREATE TABLE IF NOT EXISTS chatHistory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        imageUrl TEXT,
                        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        lastModified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

    def addMessage(self, role: str, content: str, imageUrl: Optional[str] = None):
        """
        Add a new chat message with role, content, and an optional image URL.
        """
        with self.lock:  # Ensure thread-safe access
            with self.connection:
                self.connection.execute('''
                    INSERT INTO chatHistory (role, content, imageUrl, created, lastModified)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (role, content, imageUrl))

    def updateMessage(self, messageId: int, newContent: str, newImageUrl: Optional[str] = None):
        """
        Update an existing message's content and image URL by its ID.
        """
        with self.lock:  # Ensure thread-safe access
            with self.connection:
                self.connection.execute('''
                    UPDATE chatHistory
                    SET content = ?, imageUrl = ?, lastModified = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (newContent, newImageUrl, messageId))

    def deleteMessage(self, messageId: int):
        """
        Delete a message by its ID.
        """
        with self.lock:  # Ensure thread-safe access
            with self.connection:
                self.connection.execute('''
                    DELETE FROM chatHistory WHERE id = ?
                ''', (messageId,))

    def getMessages(self, limit: Optional[int] = None, projections: Optional[List[str]] = None) -> List[Dict[str, Optional[str]]]:
        """
        Fetch all messages or a limited number of messages with specified projections.
        """
        if projections is None:
            projections = ['id', 'role', 'content', 'imageUrl', 'created', 'lastModified']

        projections_str = ', '.join(projections)
        query = f'SELECT {projections_str} FROM chatHistory'
        
        with self.lock:  # Ensure thread-safe access
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            messages = [
                {key: row[i] for i, key in enumerate(projections)}
                for row in rows
            ]
            return messages[:limit] if limit else messages

    def getLastNMessages(self, n: int, projections: Optional[List[str]] = None) -> List[Dict[str, Optional[str]]]:
        """
        Get the last n messages from the chat history with specified projections.
        """
        if projections is None:
            projections = ['id', 'role', 'content', 'imageUrl', 'created', 'lastModified']

        projections_str = ', '.join(projections)
        query = f'''
            SELECT {projections_str} FROM chatHistory
            ORDER BY id DESC LIMIT ?
        '''
        
        with self.lock:  # Ensure thread-safe access
            cursor = self.connection.cursor()
            cursor.execute(query, (n,))
            rows = cursor.fetchall()
            return [
                {key: row[i] for i, key in enumerate(projections)}
                for row in rows
            ]

    def sliceMessages(self, start: int, end: int) -> List[Dict[str, Optional[str]]]:
        """
        Get a slice of messages from start index to end index.
        """
        with self.lock:  # Ensure thread-safe access
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT role, content, imageUrl, created, lastModified FROM chatHistory
            ''')
            rows = cursor.fetchall()
            return [
                {
                    "role": row[0],
                    "content": row[1],
                    "imageUrl": row[2],
                    "created": row[3],
                    "lastModified": row[4]
                }
                for row in rows[start:end]
            ]

    def getPrompt(
        self,
        limit: Optional[int] = None,
        userSlice: int = -1,
        assistantSlice: int = 200,
        borderPrompt: Optional[str] = None,
        ) -> str:
        """
        Retrieve the last N messages and format them as a prompt for an LLM.
        """
        messages = self.getLastNMessages(limit if limit else 10, projections=['role', 'content'])
        prompt = ""
        if borderPrompt:
            prompt += borderPrompt
        else:
            prompt += "The following is a conversation with an AI assistant.\n"
        for message in reversed(messages):  # Reverse to show oldest first
            if message['role'] == 'user':
                prompt += f"{message['role'].capitalize()}: {message['content'][:userSlice]}{'...' if userSlice != -1 else ''}\n"
            else:
                prompt += f"{message['role'].capitalize()}: {message['content'][:assistantSlice]}{'...' if assistantSlice != -1 else ''}\n"
        return prompt.strip() + "\n" + "-"*48


# Example usage
if __name__ == "__main__":
    from rich import print
    chat_db = ChatHistoryDB('chat_history.db')
    # chat_db.addMessage('user', 'Hello, how are you?')
    # chat_db.addMessage('assistant', 'I am fine, thank you!')

    # Retrieve and print the formatted prompt
    prompt = chat_db.getPrompt(limit=2)
    print(prompt)
