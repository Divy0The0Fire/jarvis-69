import sqlite3
from datetime import datetime
from typing import Any, Dict, Tuple, List, Union

class SQLiteDict:
    def __init__(self, db_name: str = 'data.sql') -> None:
        self.conn: sqlite3.Connection = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self) -> None:
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS data (
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (key)
                )
            ''')

    def get(self, key: str, default: Any = None) -> Any:
        """Get the value for the given key, or return the default value if not found."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM data WHERE key = ?', (key,))
        result = cursor.fetchone()
        if result is None:
            return default
        value_str = result[0]
        try:
            return eval(value_str)  # Evaluate the string to get the original value
        except Exception as e:
            print(f"Error evaluating value: {value_str}. Error: {e}")
            return None
    
    def __setitem__(self, key: str, value: Union[str, int, float, bool, tuple, list, dict, set, bytes]) -> None:
        """Set the value for the given key, converting it to a string for storage."""
        value_str = repr(value)  # Convert the value to a string representation
        with self.conn:
            self.conn.execute('''
                INSERT INTO data (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = ?, last_updated = ?
            ''', (key, value_str, value_str, datetime.now()))

    def __getitem__(self, key: str) -> Any:
        """Get the value for the given key, converting it back to its original type."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM data WHERE key = ?', (key,))
        result = cursor.fetchone()
        if result is None:
            raise KeyError(f"Key '{key}' not found.")
        value_str = result[0]
        try:
            return eval(value_str)  # Evaluate the string to get the original value
        except Exception as e:
            print(f"Error evaluating value: {value_str}. Error: {e}")
            return None

    def __delitem__(self, key: str) -> None:
        """Delete the value for the given key."""
        with self.conn:
            cursor = self.conn.execute('DELETE FROM data WHERE key = ?', (key,))
            if cursor.rowcount == 0:
                raise KeyError(f"Key '{key}' not found.")

    def __contains__(self, key: str) -> bool:
        """Check if the key exists."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM data WHERE key = ?', (key,))
        return cursor.fetchone() is not None

    def keys(self) -> List[str]:
        """Return all keys."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT key FROM data')
        return [row[0] for row in cursor.fetchall()]

    def items(self) -> List[Tuple[str, Any]]:
        """Return all key-value pairs."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT key, value FROM data')
        return [(key, eval(value)) for key, value in cursor.fetchall()]

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

    def __str__(self) -> str:
        return str({key: eval(value) for key, value in self.items()})

# Example usage
if __name__ == '__main__':
    db_dict = SQLiteDict()

    # Adding items
    db_dict['key1'] = 'value1'
    db_dict['key24'] = 42  # Storing an integer
    db_dict['key3'] = [1, 2, 3]  # Storing a list

    print(db_dict.get("key1"))
    print(db_dict.get("key33"))
    
    # Retrieving items
    print(db_dict['key1'])  # Output: value1
    print(db_dict['key24'])  # Output: 42
    print(db_dict['key3'], type(db_dict['key3']))  # Output: [1, 2, 3]
    
    # Checking existence
    print('key1' in db_dict)  # Output: True
    print('key3' in db_dict)  # Output: True
    print('key4' in db_dict)  # Output: False

    # Deleting an item
    del db_dict['key24']
    # Listing all keys
    print(db_dict.items())  # Output: [('key1', 'value1'), ('key3', [1, 2, 3])]

    # Closing the database
    db_dict.close()
