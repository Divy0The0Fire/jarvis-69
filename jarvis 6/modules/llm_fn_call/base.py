from dataclasses import dataclass


@dataclass
class Fn:
    name: str
    discription: str
    args: list
    kwargs: dict
