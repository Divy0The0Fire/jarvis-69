from typing import Callable, Any
from dataclasses import dataclass
from enum import Enum


class Role(Enum):
    system = "system"
    user = "user"
    assistant = "assistant"

@dataclass
class File:
    path: str
    cache: bool = True
    @property
    def text(self) -> str:
        if not self.cache:
            with open(self.path, "rb") as f:
                return f.read().decode("utf-8")
        elif self.cache and isinstance(self.cache, bool):
            with open(self.path, "rb") as f:
                self.cache = f.read().decode("utf-8")
        return self.cache

@dataclass
class Text:
    text: str

@dataclass
class Image:
    text: str
    url: str

class Function:
    def __init__(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def __call__(self) -> Any:
        return self.func(*self.args, **self.kwargs)