import torch
import torch.nn.functional as F
import sqlite3
import io
from transformers import AutoTokenizer, AutoModel
from typing import List, Tuple, Optional
from pathlib import Path
from rich import print

class VectorSearch:
    def __init__(self, modelPath: str = 'Alibaba-NLP/gte-large-en-v1.5', dbFile: Optional[str] = 'vector_store.db'):
        # Initialize model, tokenizer, and database
        self.tokenizer = AutoTokenizer.from_pretrained(modelPath)
        self.model = AutoModel.from_pretrained(modelPath, trust_remote_code=True)
        self.dbFile = dbFile
        
        # Initialize SQLite database
        self._init_db()
        
        # Cache for embeddings and documents during runtime
        self.documentEmbeddings: List[torch.Tensor] = []
        self.documents: List[str] = []
        self._load_from_db()

    def _init_db(self) -> None:
        # Initialize SQLite database with required tables
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document TEXT NOT NULL,
                embedding BLOB NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _tensor_to_blob(self, tensor: torch.Tensor) -> bytes:
        # Convert tensor to bytes for storage
        buffer = io.BytesIO()
        torch.save(tensor, buffer)
        return buffer.getvalue()

    def _blob_to_tensor(self, blob: bytes) -> torch.Tensor:
        # Convert bytes back to tensor
        buffer = io.BytesIO(blob)
        return torch.load(buffer)

    def _load_from_db(self) -> None:
        # Load all embeddings and documents from database
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()
        cursor.execute('SELECT document, embedding FROM embeddings')
        rows = cursor.fetchall()
        
        self.documents = []
        self.documentEmbeddings = []
        for doc, emb_blob in rows:
            self.documents.append(doc)
            self.documentEmbeddings.append(self._blob_to_tensor(emb_blob))
        
        conn.close()

    def getEmbedding(self, text: str) -> torch.Tensor:
        # Generate and normalize embedding for a given text
        batchDict = self.tokenizer([text], max_length=8192, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            outputs = self.model(**batchDict)
        embedding = outputs.last_hidden_state[:, 0]
        return F.normalize(embedding, p=2, dim=1).cpu()
    
    def addText(self, text: str) -> None:
        # Add a single text to the index and save to database
        embedding = self.getEmbedding(text)
        
        # Save to database
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO embeddings (document, embedding) VALUES (?, ?)',
                      (text, self._tensor_to_blob(embedding)))
        conn.commit()
        conn.close()
        
        # Update runtime cache
        self.documentEmbeddings.append(embedding)
        self.documents.append(text)
    
    def addTexts(self, texts: List[str]) -> None:
        # Add multiple texts to the index in bulk
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()
        
        for text in texts:
            embedding = self.getEmbedding(text)
            cursor.execute('INSERT INTO embeddings (document, embedding) VALUES (?, ?)',
                         (text, self._tensor_to_blob(embedding)))
            self.documentEmbeddings.append(embedding)
            self.documents.append(text)
        
        conn.commit()
        conn.close()

    def retrieve(self, query: str, topK: int = 2) -> List[Tuple[str, float]]:
        # Retrieve topK documents most similar to the query
        queryEmbedding = self.getEmbedding(query)
        scores = [
            (self.documents[i], (queryEmbedding @ docEmb.T).item())
            for i, docEmb in enumerate(self.documentEmbeddings)
        ]
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[:topK]
        return scores

    def retrieveWithThreshold(self, query: str, threshold: float) -> List[Tuple[str, float]]:
        # Retrieve documents that have similarity scores above a certain threshold
        queryEmbedding = self.getEmbedding(query)
        scores = [
            (self.documents[i], (queryEmbedding @ docEmb.T).item())
            for i, docEmb in enumerate(self.documentEmbeddings)
        ]
        return [(doc, score) for doc, score in scores if score >= threshold]

    def updateText(self, oldText: str, newText: str) -> None:
        # Update an existing text in the index with a new one
        if oldText in self.documents:
            idx = self.documents.index(oldText)
            newEmbedding = self.getEmbedding(newText)
            self.documents[idx] = newText
            self.documentEmbeddings[idx] = newEmbedding
            
            # Update database
            conn = sqlite3.connect(self.dbFile)
            cursor = conn.cursor()
            cursor.execute('UPDATE embeddings SET document = ?, embedding = ? WHERE document = ?',
                          (newText, self._tensor_to_blob(newEmbedding), oldText))
            conn.commit()
            conn.close()

    def removeText(self, text: str) -> None:
        # Remove a specific text and its embedding from the index
        if text in self.documents:
            idx = self.documents.index(text)
            self.documents.pop(idx)
            self.documentEmbeddings.pop(idx)
            
            # Update database
            conn = sqlite3.connect(self.dbFile)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM embeddings WHERE document = ?', (text,))
            conn.commit()
            conn.close()

    def getAllTexts(self) -> List[str]:
        # Retrieve all stored texts/documents
        return self.documents

    def getAllEmbeddings(self) -> List[torch.Tensor]:
        # Retrieve all stored embeddings
        return self.documentEmbeddings

    def clearIndex(self) -> None:
        # Clear all documents and embeddings
        self.documents.clear()
        self.documentEmbeddings.clear()
        
        # Clear database
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM embeddings')
        conn.commit()
        conn.close()

# Usage example
if __name__ == "__main__":
    # Initialize the search system
    vectorSearch = VectorSearch(dbFile="waf.db")
    
    # Adding documents
    vectorSearch.addText("male")
    vectorSearch.addText("female")
    
    # Adding multiple documents at once
    vectorSearch.addTexts(["cat", "dog", "animal", "bee"])

    # Retrieve example
    query = "set"
    topDocs = vectorSearch.retrieve(query)
    print("Top documents:", topDocs)

    # Retrieve with threshold
    thresholdDocs = vectorSearch.retrieveWithThreshold(query, threshold=0.5)
    print("Documents with score above threshold:", thresholdDocs)

    # Update text example
    vectorSearch.updateText("animal", "wildlife")

    # Remove text example
    vectorSearch.removeText("bee")

    # Get all texts example
    allTexts = vectorSearch.getAllTexts()
    print("All documents:", allTexts)

    # Clear index example
    vectorSearch.clearIndex()
