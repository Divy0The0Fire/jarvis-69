import sqlite3
import time
import typing

class SqlQueue:
    def __init__(self, db_file: str, valid_datatypes: list = None):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        
        self.valid_datatypes = [str, int, float, bool, tuple, list, dict, set, bytes] \
            if not valid_datatypes else valid_datatypes
        
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY,
                    value TEXT NOT NULL,
                    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def put(self, value: str | int | float | bool | tuple | list | dict | set | bytes):
        if not isinstance(value, tuple(self.valid_datatypes)):
            raise ValueError(f"Value must be one of the following types: {self.valid_datatypes}")
        
        # Convert value to string for storage
        self.cursor.execute("INSERT INTO queue (value) VALUES (?)", (repr(value),))
        self.conn.commit()

    def get(self, block: bool = True, timeout: int = None) -> typing.Any:
        sttime = time.time()

        while True:
            self.cursor.execute("SELECT id, value FROM queue ORDER BY timestamp ASC LIMIT 1")
            row = self.cursor.fetchone()

            if row is not None:
                row_id, value = row
                self.cursor.execute("DELETE FROM queue WHERE id = ?", (row_id,))
                self.conn.commit()
                try:
                    return eval(value)
                except Exception as e:
                    print(e)
                    print(f"Value: {value}")
                    print(f"Type: {type(value)}")
                    return None

            if not block:
                return None
            if timeout is not None and time.time() - sttime > timeout:
                break
        return None
    
    
if __name__ == "__main__":
    q = SqlQueue("data.db")
    sample_data = ["Hello", 42, 3.14, True, (1, 2, 3), [1, 2, 3], {"a": 1, "b": 2}, {1, 2, 3}, b"Hello"]
    for i in sample_data:
        q.put(i)
        time.sleep(0.01)

    q.put("STOP")

    for i in range(100):
        print(q.get(timeout=0.1),)
