import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cdist

class SimpleVectorDB:
    def __init__(self):
        # Initialize the embedding model and storage
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Small, fast embedding model
        self.vectors = []  # Store vectors (embeddings)
        self.texts = []  # Store original texts

    def add_text(self, text):
        """Convert text to embedding and store it."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        self.vectors.append(embedding)
        self.texts.append(text)
    
    def query(self, query_text, top_k=3):
        """Query the database for similar texts based on the input query."""
        # Convert query to embedding
        query_embedding = self.model.encode(query_text, convert_to_numpy=True)
        
        if len(self.vectors) == 0:
            print("No vectors in database.")
            return []

        # Calculate cosine similarity between query and stored vectors
        similarities = 1 - cdist([query_embedding], self.vectors, metric='cosine')[0]
        
        # Get the indices of the top_k most similar vectors
        top_k_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return the top_k most similar texts and their similarities
        return [(self.texts[idx], similarities[idx]) for idx in top_k_indices]

# Example usage
if __name__ == "__main__":
    # Initialize the vector database
    db = SimpleVectorDB()
    
    # Add some example texts
    db.add_text("This is a sample sentence about AI.")
    db.add_text("We are building a vector database.")
    db.add_text("Vector databases are useful for storing embeddings.")
    
    # Query the database with a new sentence
    results = db.query("Tell me about AI and databases.", top_k=3)
    
    # Output the results
    for result in results:
        print(f"Text: {result[0]}, Similarity: {result[1]:.4f}")
