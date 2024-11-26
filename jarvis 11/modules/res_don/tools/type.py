import os
from typing import Optional
from enum import Enum


class TextSlice:
    def __init__(self, start: float | int, end: float | int):
        """
        Slice the text by start and end indices.

        Parameters
        ----------
        start : float or int
            The start index of the slice. If float, represents a percentage of text length.
        end : float or int
            The end index of the slice. If float, represents a percentage of text length.

        Examples
        --------
        >>> TextSlice(.1, -.5)("1234567890")
        '12345'
        >>> TextSlice(1, -1)("1234567890")
        '23456789'
        """
        self.start = start
        self.end = end
    
    def __repr__(self) -> str:
        return f"TextSlice(start={self.start}, end={self.end})"
    
    def __call__(self, text: str) -> str:
        text_length = len(text)
        
        # Handle start index
        if isinstance(self.start, float):
            start = int(text_length * self.start)
        else:
            start = self.start
        # Convert negative start index
        if start < 0:
            start = text_length + start
            
        # Handle end index
        if isinstance(self.end, float):
            end = int(text_length * self.end)
        else:
            end = self.end
        # Convert negative end index
        if end < 0:
            end = text_length + end
            
        # If end is 0, convert it to None to slice until the end of string
        if end == 0:
            end = None
            
        return text[start:end]




def isTextFileByPath(filePath: str) -> bool | None:
    """
    Check if a file is a text file by attempting to read it.

    Parameters
    ----------
    filePath : str
        Path to the file to check.

    Returns
    -------
    bool or None
        True if file is readable as text,
        False if file is not readable as text,
        None if file is not found or permission denied.
    """
    try:
        with open(filePath, 'r', encoding='utf-8') as file:
            file.read()
            return True
    except (FileNotFoundError, PermissionError):
        return None
    except UnicodeDecodeError:
        return False

def listAllTextFilesInDir(dirPath: str) -> list[str]:
    """
    List all text files in a directory and its subdirectories.

    Parameters
    ----------
    dirPath : str
        Path to the directory to search.

    Returns
    -------
    list of str
        List of paths to all text files found.
    """
    text_files = []
    for root, dirs, files in os.walk(dirPath):
        for file in files:
            if isTextFileByPath(os.path.join(root, file)):
                text_files.append(os.path.join(root, file))
    return text_files


if __name__ == "__main__":
    from rich import print
    # print(listAllTextFilesInDir(r"data"))
    # getting last 5 characters
    print(TextSlice(-.5, 0)("1234567890"))
