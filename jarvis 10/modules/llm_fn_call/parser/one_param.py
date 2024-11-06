import ast
from typing import List
from dataclasses import dataclass
from rich import print

@dataclass
class Function:
    name: str
    args: tuple
    kwargs: dict

def parseFunctionString(functionString: str) -> List[Function]:
    """
    Parse a function string into a list of Function objects.
    
    Example:
    ```python
    result = parseFunctionString("prime(1, 2, q='hoe'), nonexistent_func(1, 2, x='test')")
    print(result)
    # Output:
    # [Function(name='prime', args=(1, 2), kwargs={'q': 'hoe'}), Function(name='nonexistent_func', args=(1, 2), kwargs={'x': 'test'})]
    ```
    """
    
    try:
        # Wrap the function calls in a tuple to make it a valid expression
        wrappedFunctionString = f"({functionString})"
        parsed = ast.parse(wrappedFunctionString)
        
        results: List[Function] = []
        if isinstance(parsed.body[0], ast.Expr) and isinstance(parsed.body[0].value, ast.Tuple):
            for call in parsed.body[0].value.elts:
                if isinstance(call, ast.Call):
                    func_name = call.func.id
                    args = tuple(ast.literal_eval(arg) for arg in call.args)
                    kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
                    
                    function_obj = Function(name=func_name, args=args, kwargs=kwargs)
                    results.append(function_obj)
                else:
                    raise ValueError("Invalid function call")
        else:
            raise ValueError("Invalid function call string")
        
        return results
    
    except Exception as e:
        print(f"Error in parseFunctionString: {str(e)}")
        return []

if __name__ == "__main__":
    # Example usage
    r = parseFunctionString('prime(1, 2, q="hoe"),nonexistent_func(1, 2, x="test")')
    print(r)
