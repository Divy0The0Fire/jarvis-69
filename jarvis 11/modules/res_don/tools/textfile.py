import os
import sys

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.getcwd())

from type import TextSlice
from textwrap import dedent
from splitters import RecursiveCharacterTextSplitter

from vector_database import VectorSearch


MAX_VISIBLE_CHARS_LENGTH: int = 50_000 # ≈ 12500 Tokens
DEFAULT_TEXT_SLICES: list[TextSlice] = [TextSlice(0, 400), ..., TextSlice(-400, 0)]

SPLITTER = RecursiveCharacterTextSplitter(chunkSize=1200, chunkOverlap=200) # Optimized for accuracy

ALLOWED_EXTENSIONS = {
    "txt",
    "py",
    "md"
}

class TextFile:
    def __init__(
        self,
        name: str,
        path: str,
        content: str,
        maxVisibleCharsLength: int = MAX_VISIBLE_CHARS_LENGTH,
        textSlices: list[TextSlice] = DEFAULT_TEXT_SLICES,
        ):
        """
        Initialize a TextFile object.

        Parameters
        ----------
        name : str
            Name of the text file.
        path : str
            Path to the text file.
        content : str
            Content of the text file.

        Attributes
        ----------
        linesCount : int
            Number of lines in the file.
        charsCount : int
            Total number of characters in the file.
        wordsCount : int
            Total number of words in the file.
        """
        self.name = name
        self.path = path
        self.content = content
        self.maxVisibleCharsLength = maxVisibleCharsLength
        self.textSlices = textSlices
        
        self.linesCount = content.count("\n") + 1
        self.charsCount = len(content)
        self.wordsCount = len(content.split())
        self.isRag = True if self.charsCount > self.maxVisibleCharsLength else False
        self.vectorSearch = VectorSearch() if self.isRag else None
        
        # self._splitContent()
        self._addContentToVectorSearch()



    def _splitContent(self) -> list[str]:
        return SPLITTER.splitText(self.content)
    
    def _addContentToVectorSearch(self) -> None:
        if self.isRag:
            for chunk in self._splitContent():
                self.vectorSearch.addText(chunk)

    def searchByQuery(self, query: str, topK: int = 5) -> list[tuple[float, str]]:
        """
        Search through the text content using a semantic query.
        
        This method performs a semantic search on the text content if RAG (Retrieval-Augmented Generation)
        is enabled (i.e., if the text content is longer than maxVisibleCharsLength). It uses the
        vector database to find the most relevant text chunks that match the query.
        
        Parameters
        ----------
        query : str
            The search query to find relevant text chunks
        topK : int, optional
            Number of top matching results to return (default is 5)
        
        Returns
        -------
        list[tuple[float, str]]
            A list of tuples containing (score, text_chunk)
            - score: float indicating the relevance (higher is better)
            - text_chunk: str containing the matching text segment
            Returns empty list if RAG is not enabled
        
        Examples
        --------
        >>> text_file = TextFile("example.txt", "/path/to/file", "Long text content...")
        >>> results = text_file.searchByQuery("specific topic", topK=3)
        >>> for score, chunk in results:
        ...     print(f"Score: {score:.2f}")
        ...     print(f"Text: {chunk}\n")
        """
        if self.isRag:
            return self.vectorSearch.retrieve(query, topK=topK)
        else:
            return []

    def __repr__(self) -> str:
        return dedent(f"""
        TextFile(
            name={self.name},
            path={self.path},
            linesCount={self.linesCount},
            charsCount={self.charsCount},
            wordsCount={self.wordsCount},
            maxVisibleCharsLength={self.maxVisibleCharsLength},
            textSlices={self.textSlices}
        )
        """)
    
    def __call__(self) -> str:
        """
        Returns the content of the text file, with a maximum of maxVisibleCharsLength characters.
        If the content is longer than maxVisibleCharsLength, it will be truncated and a message will be displayed.
        
        Examples
        --------
        >>> text_file = TextFile("example.txt", "/path/to/file", "Long text content...")
        >>> print(text_file())
        Long text content...
        """
        if self.charsCount <= self.maxVisibleCharsLength:
            return self.content
        else:
            content = ""
            for textSlice in self.textSlices:
                if isinstance(textSlice, TextSlice):
                    content += textSlice(self.content) + "\n"
                elif textSlice is ...:
                    hidden_chars = self.charsCount - sum(len(ts(self.content)) for ts in self.textSlices if isinstance(ts, TextSlice))
                    visible_lines = sum(ts(self.content).count('\n') for ts in self.textSlices if isinstance(ts, TextSlice))
                    hidden_lines = max(0, self.linesCount - visible_lines)
                    content += f"\n{'-' * 48}\n[... {hidden_chars:,} hidden characters, {hidden_lines:,} lines ...]\n{'-' * 48}\n\n"

            return content



def local_to_global_import():
    import sentence_transformers
    globals()["sentence_transformers"] = sentence_transformers


local_to_global_import()
if __name__ == "__main__":
    from rich import print
    print(TextFile("test", "test", "test\n"*500))
