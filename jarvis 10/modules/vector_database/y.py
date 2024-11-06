import requests
from rich import print

url = "https://divy118-stella-text-embedding.hf.space/embeddings/"
token = ""  # Replace with the actual token
headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

# Define the payload with input sentences and embedding type
data = {
    "input": ["This is a test sentence.", "Here is another example sentence."],
    "embedding_type": "s2p_query"  # or "s2s_query" depending on your need
}

response = requests.post(url, json=data, headers=headers)

# Check if the request was successful and print the response
if response.status_code == 200:
    embeddings = response.json()
    print("Embeddings:", len(embeddings[1]))
else:
    print("Error:", response.status_code, response.json())
