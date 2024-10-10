import cohere
from rich import print

co = cohere.ClientV2("FIpCfF2pfLI8sp4pBnHkOfXjmas71bOpZTijLB6D")

response = co.chat_stream(
    model="command-r-plus-08-2024",
    messages=[
        {
            "role": "user",
            "content": "2+2"
        }
    ]
)

print(*response)
