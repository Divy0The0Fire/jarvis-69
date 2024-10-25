from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TextVector:
    text: str
    vector: list
    metadata: Optional[Dict[str, str]] = None


