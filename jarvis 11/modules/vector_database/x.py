import torch
import torch.nn.functional as F
import pickle
from transformers import AutoTokenizer, AutoModel
from typing import List, Tuple, Dict, Optional, Union
from pathlib import Path
from rich import print

class VectorSearch:
    def __init__(self, model_path: str = 'Alibaba-NLP/gte-large-en-v1.5', embedding_file: str = "embeddings.pkl"):
        # Initialize model, tokenizer, and embedding storage file path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
        self.embedding_file = Path(embedding_file)
        
        # Load existing embeddings or initialize empty storage
        self.document_embeddings: List[torch.Tensor] = []
        self.documents: List[str] = []
        if self.embedding_file.exists():
            self._load_embeddings()

    def _load_embeddings(self) -> None:
        # Load embeddings and documents from a local file
        with open(self.embedding_file, 'rb') as f:
            data = pickle.load(f)
            self.document_embeddings, self.documents = data['embeddings'], data['documents']

    def _save_embeddings(self) -> None:
        # Save embeddings and documents to a local file
        with open(self.embedding_file, 'wb') as f:
            pickle.dump({'embeddings': self.document_embeddings, 'documents': self.documents}, f)

    def get_embedding(self, text: str) -> torch.Tensor:
        # Generate and normalize embedding for a given text
        batch_dict = self.tokenizer([text], max_length=8192, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            outputs = self.model(**batch_dict)
        embedding = outputs.last_hidden_state[:, 0]
        return F.normalize(embedding, p=2, dim=1).cpu()
    
    def add_text(self, text: str) -> None:
        # Add a single text to the index and save embeddings
        embedding = self.get_embedding(text)
        self.document_embeddings.append(embedding)
        self.documents.append(text)
        self._save_embeddings()
    
    def add_texts(self, texts: List[str]) -> None:
        # Add multiple texts to the index in bulk and save embeddings
        embeddings = [self.get_embedding(text) for text in texts]
        self.document_embeddings.extend(embeddings)
        self.documents.extend(texts)
        self._save_embeddings()

    def retrieve(self, query: str, top_k: int = 2) -> List[Tuple[str, float]]:
        # Retrieve top_k documents most similar to the query
        query_embedding = self.get_embedding(query)
        scores = [
            (self.documents[i], (query_embedding @ doc_emb.T).item())
            for i, doc_emb in enumerate(self.document_embeddings)
        ]
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]
        return scores

    def retrieve_with_threshold(self, query: str, threshold: float) -> List[Tuple[str, float]]:
        # Retrieve documents that have similarity scores above a certain threshold
        query_embedding = self.get_embedding(query)
        scores = [
            (self.documents[i], (query_embedding @ doc_emb.T).item())
            for i, doc_emb in enumerate(self.document_embeddings)
        ]
        return [(doc, score) for doc, score in scores if score >= threshold]

    def update_text(self, old_text: str, new_text: str) -> None:
        # Update an existing text in the index with a new one
        if old_text in self.documents:
            idx = self.documents.index(old_text)
            new_embedding = self.get_embedding(new_text)
            self.documents[idx] = new_text
            self.document_embeddings[idx] = new_embedding
            self._save_embeddings()

    def remove_text(self, text: str) -> None:
        # Remove a specific text and its embedding from the index
        if text in self.documents:
            idx = self.documents.index(text)
            self.documents.pop(idx)
            self.document_embeddings.pop(idx)
            self._save_embeddings()

    def get_all_texts(self) -> List[str]:
        # Retrieve all stored texts/documents
        return self.documents

    def get_all_embeddings(self) -> List[torch.Tensor]:
        # Retrieve all stored embeddings
        return self.document_embeddings

    def clear_index(self) -> None:
        # Clear all documents and embeddings
        self.documents.clear()
        self.document_embeddings.clear()
        self._save_embeddings()

# Usage example
if __name__ == "__main__":
    # Initialize the search system
    vector_search = VectorSearch()
    
    # Adding documents
    vector_search.add_text("male")
    vector_search.add_text("female")
    
    # Adding multiple documents at once
    vector_search.add_texts(["cat", "dog", "animal", "bee"])

    # Retrieve example
    query = "sex"
    top_docs = vector_search.retrieve(query)
    print("Top documents:", top_docs)

    # Retrieve with threshold
    threshold_docs = vector_search.retrieve_with_threshold(query, threshold=0.5)
    print("Documents with score above threshold:", threshold_docs)

    # Update text example
    vector_search.update_text("animal", "wildlife")

    # Remove text example
    vector_search.remove_text("bee")

    # Get all texts example
    all_texts = vector_search.get_all_texts()
    print("All documents:", all_texts)

    # Clear index example
    vector_search.clear_index()
