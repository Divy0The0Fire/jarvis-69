from dataclasses import dataclass, field
from typing import Dict, Optional
import re
import json

@dataclass
class Fn:
    name: str
    description: str
    parameters: Dict[str, str]
    example_input: Optional[Dict[str, str]] = field(default_factory=dict)
    example_output: Optional[str] = None

    def __post_init__(self):
        self._cached_prompt = None  # Initialize the cache

    @property
    def prompt(self) -> str:
        """Generate a formatted prompt for this individual function."""
        # Check if the prompt is already cached
        if self._cached_prompt is not None:
            return self._cached_prompt
        
        prompt = f"**`{self.name}("
        
        # Add parameters to function signature
        if self.parameters:
            params = ", ".join([f"{key}" for key in self.parameters.keys()])
            prompt += f"{params})`**\n"
        else:
            prompt += ")`**\n"
        
        prompt += f"  - **Description:** {self.description}\n"
        if self.parameters:
            prompt += f"  - **Parameters:**\n"
            for param, param_type in self.parameters.items():
                prompt += f"    - `{param}` ({param_type}): The {param}.\n"
        
        # Add example input
        if self.example_input:
            prompt += f"  - **Example:**\n"
            prompt += f"    - **Input:** `{self.example_input}`\n"
        
        # Add example output
        if self.example_output:
            prompt += f"    - **Output:** `{self.example_output}`\n"
        
        # Cache the generated prompt
        self._cached_prompt = prompt
        
        return prompt

systemPromptTemplate = """\
### Prompt:

**You are provided with a set of functions to fetch data from cloud services. Your task is to analyze the user's input and decide which functions should be called, and with what parameters. You do not execute these functions directly; instead, you provide a list of dictionaries with function names and parameters to be executed externally. Please ensure your output follows this structure.**

#### Function Definitions:

[| {functions} |]

#### Instructions for Output:

- **Do not** perform the requested tasks.
- **Do not** respond to any query directly.
- Based on the user's input, analyze which functions to call and provide their parameters.
- Return the output in the following format:

```json
[
    {
        "function": "function_name_here",
        "parameters": { "key": "value" }
    },
    {
        "function": "another_function_name",
        "parameters": {}
    }
]
```

- Each dictionary must include:
  - The **function name** (one of the five functions above).
  - The **parameters** for that function in key-value pairs (or an empty object `{}` if no parameters are required).

#### Example Scenario:

- User Input: *"What's the weather like in New York and any news today?"*

- Your Output:
```json
[
    {
        "function": "getWeather",
        "parameters": {
            "location": "New York"
        }
    },
    {
        "function": "getRecentNews",
        "parameters": {}
    }
]
```

---

**Important**: Only return the list of functions to be called and the required parameters in the structure provided. Do not return actual data from the functions—just indicate what needs to be executed.
"""


def generateSystemPrompt(functions: list[Fn]) -> str:
    """Generate a formatted prompt for the LLM."""
    fn_prompts = "\n".join([f.prompt for f in functions])
    return systemPromptTemplate.replace("[| {functions} |]", fn_prompts)


def extractJSON(text: str) -> list[dict] | None:
    """Extract JSON from a string."""
    pattern = r'```json\n(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        json_string = match.group(1)
        return json.loads(json_string)
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None

if __name__ == "__main__":
    # from rich import print
    # Creating function definitions
    functions = [
        Fn(
            name="getWeather",
            description="Fetches the current weather for a specific location.",
            parameters={"location": "string"},
            example_input={"location": "New York"},
            example_output='{"location": "New York", "temperature": "22°C", "status": "Sunny"}'
        ),
        Fn(
            name="getRecentNews",
            description="Fetches the latest news headlines.",
            parameters={},
            example_output='[{"title": "Tech news: AI advancements", "date": "2024-10-09"}]'
        ),
        Fn(
            name="getStockPrices",
            description="Fetches the current stock price for a specific stock ticker.",
            parameters={"ticker": "string"},
            example_input={"ticker": "AAPL"},
            example_output='{"ticker": "AAPL", "price": "150.30"}'
        ),
        Fn(
            name="getExchangeRates",
            description="Fetches the current exchange rate for a specific currency.",
            parameters={"currency": "string"},
            example_input={"currency": "USD"},
            example_output='{"currency": "USD", "rate": "1.13"}'
        ),
        Fn(
            name="getTrafficUpdates",
            description="Fetches the current traffic updates for a specific city.",
            parameters={"city": "string"},
        )
    ]
    print(
        Fn(
            name="getExchangeRates",
            description="Fetches the current exchange rate for a specific currency.",
            parameters={"currency": "string"},
            example_input={"currency": "USD"},
            example_output='{"currency": "USD", "rate": "1.13"}'
        ).prompt
    )
    # print(json.loads("[{'function': 'wikiSearch', 'parameters': {'query': 'hello'}}]"))
