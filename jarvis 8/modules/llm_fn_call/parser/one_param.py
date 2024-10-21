import ast
import re
from typing import List, Dict, Any

def parse_function_calls(input_string: str) -> List[List[str | Dict[str, Any]]]:
    pattern = r'(\w+)\((.*?)\)'

    matches: List[tuple[str, str]] = re.findall(pattern, input_string)

    data: List[Dict[str, Dict[str, Any]]] = []
    for func, args in matches:
        arg_pairs: List[str] = [arg.strip() for arg in args.split(',')]
        func_dict: Dict[str, Dict[str, Any]] = {func: {}}
        for arg in arg_pairs:
            key, value = arg.split('=')
            func_dict[func][key.strip()] = value.strip().strip('"')
        data.append(func_dict)

    result: List[List[str | Dict[str, Any]]] = [[list(item.keys())[0], item[list(item.keys())[0]]] for item in data]
    return result

# Input string
input_string = 'fn1(query="print(2+2)"), url(url="https://www.dominos.com/")'

# Call the function and print the result
result = parse_function_calls(input_string)
print(result)


