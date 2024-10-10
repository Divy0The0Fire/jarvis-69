import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os

def cosine_similarity(A: np.ndarray, B: np.ndarray) -> float:
    # Compute dot product of vectors A and B
    dot_product = np.dot(A.flatten(), B.flatten())
    
    # Compute L2 norms (magnitudes) of A and B
    norm_A = np.linalg.norm(A)
    norm_B = np.linalg.norm(B)
    
    # Compute cosine similarity
    return dot_product / (norm_A * norm_B)


class TextClassifier:
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L12-v2'):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.label_prototypes: dict[str, np.ndarray] = {}

    def load_data(self, file_path: str, text_column: str = 'Examples', label_column: str = 'Labels') -> tuple[list[str], list[str]]:
        data = pd.read_csv(file_path)
        sentences = data[text_column].tolist()
        labels = data[label_column].tolist()
        return sentences, labels

    def create_prototypes(self, sentences: list[str], labels: list[str]) -> None:
        embeddings = self.model.encode(sentences)
        for label in set(labels):
            label_embeddings = embeddings[np.array(labels) == label]
            self.label_prototypes[label] = np.mean(label_embeddings, axis=0)

    def classify(self, new_example: str) -> str:
        new_embedding = self.model.encode([new_example])
        similarities = {
            label: cosine_similarity(new_embedding, prototype)
            for label, prototype in self.label_prototypes.items()
        }
        predicted_label = max(similarities, key=similarities.get)
        return predicted_label


    def save_model(self, file_path: str = 'text_classifier_model.pkl') -> None:
        with open(file_path, 'wb') as f:
            pickle.dump({
                'model_name': self.model_name,
                'label_prototypes': self.label_prototypes
            }, f)
        print(f'Model saved to {file_path}')

    def load_model(self, file_path: str = 'text_classifier_model.pkl') -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            self.model_name = data['model_name']
            self.model = SentenceTransformer(self.model_name)
            self.label_prototypes = data['label_prototypes']

        print(f'Model loaded from {file_path}')


# Example usage:
if __name__ == "__main__":
    classifier = TextClassifier()
    sentences, labels = classifier.load_data(r'data/test/data.csv')
    classifier.create_prototypes(sentences, labels)
    classifier.save_model('trained_text_classifier.pkl')
    # classifier.load_model('trained_text_classifier.pkl')
    
    while True:
        new_example = input("Enter a new example: ")
        predicted_label = classifier.classify(new_example)
        print(f"The predicted label for the new example is: {predicted_label}")
