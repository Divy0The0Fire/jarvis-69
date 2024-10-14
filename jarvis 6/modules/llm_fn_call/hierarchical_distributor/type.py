from dataclasses import dataclass


@dataclass
class Fn:
    name: str
    discription: str
    docstring: str
    kwargs: dict

def get_answer(q: str) -> str:
    return "hello {}".format(q)





if __name__ == "__main__":
    # Fn(
    #     name="hello",
    #     discription="this will fuck you",
    #     docstring="this will fuck you",
    #     kwargs={},
    # )

    for i in range(10):
        print('hello', flush=True, end='')