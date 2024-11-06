openai = [
    {
      "role": "user", 
      "content": "Hello, how are you?"
    },
    {
      "role": "assistant", 
      "content": "I'm doing well, thank you!"
    },
    {
      "role": "user", 
      "content": [
        {
          "type": "text", 
          "text": "Hello, how are you?"
        },
        {
          "type": "image_url", 
          "image_url": {"url": "https://example.com/image.png"}
        },
      ]
    },
    {
        "role": "assistant",
        "content": "I'm doing well, thank you!"
    },
    {
        "role": "assistant",
        "content": "I'm doing well, thank you!"
    },
    {
        "role": "user",
        "content": "Hello, how are you?"
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Hello, how are you?"
            },
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/image.png"}
            },
            {
                "type": "text",
                "text": "Hello, how are you?"
            },
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/image.png"}
            },
        ]
    },
]

def convert_openai_to_gemini(openai_messages: list) -> list:
    """
    Convert OpenAI message format to Gemini message format.
    
    Args:
        openai_messages (list): Messages in OpenAI format
        
    Returns:
        list: Messages in Gemini format with balanced user/model interactions
    """
    def convert_image_url_to_file_reference(url: str) -> str:
        return f"FILE({url[:10]})"

    # Initial conversion to Gemini format
    gemini_messages = []
    system_messages = []

    # Convert messages to Gemini format
    for message in openai_messages:
        role = message["role"]
        content = message["content"]

        if role == "system":
            system_messages.append(content)
        elif role == "user":
            if isinstance(content, list):
                for content_item in content:
                    if content_item["type"] == "text":
                        gemini_messages.append({
                            "role": "user",
                            "parts": [content_item["text"]]
                        })
                    elif content_item["type"] == "image_url":
                        gemini_messages.append({
                            "role": "user",
                            "parts": [convert_image_url_to_file_reference(content_item["image_url"]["url"])]
                        })
            else:
                gemini_messages.append({
                    "role": "user",
                    "parts": [content]
                })
        elif role == "assistant":
            gemini_messages.append({
                "role": "model",
                "parts": [content]
            })

    # Combine consecutive messages from the same role
    consolidated_messages = []
    previous_role = None

    for message in gemini_messages:
        current_role = message["role"]
        if current_role == previous_role:
            consolidated_messages[-1]["parts"].append(message["parts"][0])
        else:
            consolidated_messages.append(message)
            previous_role = current_role

    # Balance user/model interactions by inserting empty messages
    balanced_messages = []
    previous_role = None

    for message in consolidated_messages:
        current_role = message["role"]
        if current_role == previous_role == "user":
            balanced_messages.append({
                "role": "model",
                "parts": ["\n"]
            })
            previous_role = "model"
        elif current_role == previous_role == "model":
            balanced_messages.append({
                "role": "user",
                "parts": ["\n"]
            })
            previous_role = "user"
        
        balanced_messages.append(message)
        previous_role = current_role

    return balanced_messages

# Example usage:
if __name__ == "__main__":
    from rich import print
    result = convert_openai_to_gemini(openai)
    print(result)
