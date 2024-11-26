import os
import string
from collections import defaultdict
from math import log
import re

class SearchEngine:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self._index = defaultdict(lambda: defaultdict(int))  # word -> {file: count}
        self._documents = {}  # file -> content
        self.k1 = k1
        self.b = b

    def normalize_string(self, text: str) -> str:
        text = text.lower().translate(str.maketrans('', '', string.punctuation))
        return text

    def index_file(self, file_path: str, content: str):
        self._documents[file_path] = content
        words = self.normalize_string(content).split()
        for word in words:
            self._index[word][file_path] += 1

    def index_directory(self, dir_path: str, file_types=(".txt", ".py")):
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(file_types):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            self.index_file(file_path, content)
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

    @property
    def number_of_documents(self) -> int:
        return len(self._documents)

    @property
    def avdl(self) -> float:
        return sum(len(d.split()) for d in self._documents.values()) / len(self._documents)

    def idf(self, keyword: str) -> float:
        N = self.number_of_documents
        n_kw = len(self._index[keyword])
        return log((N - n_kw + 0.5) / (n_kw + 0.5) + 1)

    def bm25(self, keyword: str) -> dict[str, float]:
        result = {}
        idf_score = self.idf(keyword)
        avdl = self.avdl
        for file, freq in self._index[keyword].items():
            numerator = freq * (self.k1 + 1)
            denominator = freq + self.k1 * (1 - self.b + self.b * len(self._documents[file].split()) / avdl)
            result[file] = idf_score * numerator / denominator
        return result

    def search(self, query: str) -> dict[str, float]:
        keywords = self.normalize_string(query).split()
        url_scores = defaultdict(float)
        for kw in keywords:
            kw_scores = self.bm25(kw)
            for file, score in kw_scores.items():
                url_scores[file] += score
        return dict(sorted(url_scores.items(), key=lambda item: item[1], reverse=True))

# Main execution
if __name__ == "__main__":
    # Initialize search engine
    engine = SearchEngine()

    # Index files in a directory
    directory_to_index = os.getcwd()  # Set to your directory path
    engine.index_directory(directory_to_index)
    
    # docs = [
    #     "hello world",
    #     "how are you",
    #     "i am fine",
    #     "i am also fine",
    # ]
    # docs_ids = [
    #     1,
    #     2,
    #     3,
    #     4,
    # ]
    # for doc, doc_id in zip(docs, docs_ids):
    #     engine.index_file(doc_id, doc)
    
    # Search for a query
    query = "asyncTextToAudioPrint"  # Replace with your search terms
    results = engine.search(query)
    print("Search Results:")
    for file, score in results.items():
        print(f"{file}: {score:.4f}")
