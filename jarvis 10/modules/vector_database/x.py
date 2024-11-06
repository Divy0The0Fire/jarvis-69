from transformers import AutoTokenizer, AutoModel
from rich import print
import torch.nn.functional as F
import torch

# Initialize model and tokenizer
model_path = 'Alibaba-NLP/gte-large-en-v1.5'
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModel.from_pretrained(model_path, trust_remote_code=True)

def get_embedding(text):
    # Tokenize and get embedding
    batch_dict = tokenizer([text], max_length=8192, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**batch_dict)
    embedding = outputs.last_hidden_state[:, 0]
    return F.normalize(embedding, p=2, dim=1)

# Example documents to index
documents = [
    "male",
    "female",
]

# Generate and store embeddings for each document (using a vector database or list)
document_embeddings = [get_embedding(doc).cpu() for doc in documents]
def retrieve(query, document_embeddings, documents, top_k=2):
    query_embedding = get_embedding(query).cpu()
    scores = [(i, (query_embedding @ doc_emb.T).item()) for i, doc_emb in enumerate(document_embeddings)]
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]
    return [(documents[i], score) for i, score in scores]

# Example query
query = "pizza"
top_docs = retrieve(query, document_embeddings, documents)
print("Top documents:", top_docs)
