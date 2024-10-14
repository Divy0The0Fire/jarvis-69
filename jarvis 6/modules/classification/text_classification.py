from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
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

    def eqload_data(self, file_path: str, text_column: str = 'Examples', label_column: str = 'Labels') -> tuple[list[str], list[str]]:
        # Load the dataset
        data = pd.read_csv(file_path)
        
        # Find the minimum count of examples for any label
        min_count = data[label_column].value_counts().min()
        
        # Downsample each group to match the size of the minority label
        downsampled_data = pd.concat([
            group.sample(n=min_count, random_state=42)  # Downsample to min_count
            for label, group in data.groupby(label_column)
        ])
        
        # Shuffle the downsampled data to mix examples from different labels
        downsampled_data = downsampled_data.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Extract the sentences and labels
        sentences = downsampled_data[text_column].tolist()
        labels = downsampled_data[label_column].tolist()
        
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
    
    def advance_classify(self, new_example: str) -> tuple[str, dict[str, float]]:
        """
        Classify the new example and return the predicted label along with distances
        (cosine similarities) for all labels.
        
        :param new_example: The new text input to classify.
        :return: A tuple containing the predicted label and a dictionary with the
                cosine similarity scores for all labels.
        """
        # Encode the new example into an embedding
        new_embedding = self.model.encode([new_example])
        
        # Calculate the cosine similarity for all label prototypes
        similarities = {
            label: cosine_similarity(new_embedding, prototype)
            for label, prototype in self.label_prototypes.items()
        }
        
        # Find the label with the highest cosine similarity
        predicted_label = max(similarities, key=similarities.get)
        
        # Return the predicted label and all similarity scores (distances)
        return predicted_label, similarities
    

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
    from rich import print
    classifier = TextClassifier()
    sentences, labels = classifier.eqload_data(r'data/test/data.csv')
    classifier.create_prototypes(sentences, labels)
    classifier.save_model('trained_text_classifier.pkl')
    # classifier.load_model('trained_text_classifier.pkl')
    
    while True:
        new_example = input("Enter a new example: ")
        predicted_label = classifier.advance_classify(new_example)
        print(f"The predicted label for the new example is: {predicted_label}")
