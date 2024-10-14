from typing import Dict, Optional, Callable, Union, Any, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed

import io
import os

try:
    from modules.prompt.type import Text, Image, Function, Role, File
except ImportError:
    
    import sys
    sys.path.append(os.path.dirname(__file__))
    from type import Text, Image, Function, Role, File

# Dynamically determine the number of CPU cores
def getMaxWorkers() -> int:
    # Get the number of CPUs
    cpu_count = os.cpu_count()
    # Return a suitable number of workers (cpu_count or a formula based on it)
    return max(1, cpu_count)  # At least 1 worker, even if os.cpu_count() returns None

def getMessage(role: Role, content: str, imageUrl: Optional[str] = None) -> Dict[str, Any]:
    role = Role[role] if isinstance(role, str) else role
    message: Dict[str, Union[str, list]] = {"role": role.value, "content": []}
    if imageUrl:
        message["content"].append({"type": "image_url", "image_url": {"url": imageUrl}})
    
    if content:
        if len(message["content"]) > 0:
            message["content"].append({"type": "text", "text": content})
        else:
            return {"role": role.value, "content": content}

    return message

class Prompt:
    def __init__(
        self,
        role: Role = Role.system,
        template: List[Union[Text, Image, Callable, Function]] = [],
        separator: str = "\n",
        maxWorkers: int = 4,
        cheatCode: Optional[str] = None
    ):
        self.role = role
        self.template = template
        self.separator = separator
        self.cheatCode = cheatCode

        if cheatCode is not None:
            print("cheatCode:", cheatCode)
            self.max_workers = getMaxWorkers() * abs(max([maxWorkers, len(cheatCode)]) if cheatCode.isnumeric() == False else int(cheatCode))
        else:
            self.max_workers = maxWorkers  # Thread pool workers limit
    @property
    def promptWithImages(self) -> Tuple[str, List[str]]:
        """
        Sequentially processes the template without concurrency.
        """
        if self.cheatCode is not None:
            return self.fastprompt

        prompt = ""
        images = []
        
        for element in self.template:
            processed = self.processRawTexts(element)
            if isinstance(processed, Image):
                images.append(getMessage(self.role, processed.text, processed.url))
            else:
                prompt += processed + self.separator

        return prompt, images
    
    @property
    def fastpromptWithImages(self) -> Tuple[str, List[str]]:
        """
        Concurrently processes callable elements (Function) using a ThreadPoolExecutor
        for faster performance, especially when dealing with multiple callables.
        """
        prompt = ""
        images = []
        
        # Collect all callable elements that need to be processed in parallel
        futures = []
        non_callable_elements = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for element in self.template:
                if isinstance(element, Function):  # If it's a callable, use the thread pool
                    futures.append(executor.submit(self.processRawTexts, element))
                elif isinstance(element, Prompt):
                    rawPrompt, rawImages = element.fastprompt
                    prompt += rawPrompt
                    images += rawImages
                else:
                    non_callable_elements.append(self.processRawTexts(element))
        
        # Wait for all callables to complete and gather their results
        for future in as_completed(futures):
            non_callable_elements.append(future.result())

        # Process non-callable elements and append to prompt
        for processed in non_callable_elements:
            if isinstance(processed, Image):
                images.append(getMessage(self.role, processed.text, processed.url))
            else:
                prompt += processed + self.separator

        return prompt, images

    
    @property
    def prompt(self) -> str:
        """
        Sequentially processes the template without concurrency.
        """
        return self.promptWithImages[0]
    
    @property
    def fastprompt(self) -> Tuple[str, List[str]]:
        """
        Concurrently processes callable elements (Function) using a ThreadPoolExecutor
        for faster performance, especially when dealing with multiple callables.
        """
        return self.fastpromptWithImages[0]

    def processRawTexts(self, element: Any) -> Union[str, Image]:
        """
        Return prompt or image URLs depending on the type of element.
        """
        if isinstance(element, (Text, File)):
            return element.text
        elif isinstance(element, str):
            return element
        elif isinstance(element, Function):
            output = element()
            return self.processRawTexts(output)
        elif isinstance(element, Image):
            return element

        output = io.StringIO()
        print(element, file=output)
        return output.getvalue()

    def __call__(self, use_fast: bool = False) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Depending on the `use_fast` flag, it will either use the regular sequential
        `prompt` method or the concurrent `fastprompt` method.
        """
        if use_fast:
            return self.fastprompt
        return self.prompt

if __name__ == "__main__":
    import time
    from time import sleep

    # Simulate a time-consuming task
    def slow_function_1():
        sleep(2)  # Simulate 2 seconds of work
        return "Result from slow_function_1"

    def slow_function_2():
        sleep(3)  # Simulate 3 seconds of work
        return "Result from slow_function_2"

    # Instantiate the Prompt class
    prompt_template = [
        Text("This is a regular text element."),
        Function(slow_function_1),  # This will take 2 seconds to run
        Text("Another regular text element."),
        Function(slow_function_2),  # This will take 3 seconds to run
        Image("Here is an image", "https://example.com/image.jpg")
    ]

    prompt_instance = Prompt(role=Role.user, template=prompt_template)

    # Test sequential prompt method
    print("Testing sequential prompt (prompt):")
    start_time = time.time()
    prompt_result, images = prompt_instance()  # Sequential processing
    end_time = time.time()
    print(f"Sequential prompt output:\n{prompt_result}")
    print(f"Images: {images}")
    print(f"Time taken (sequential): {end_time - start_time:.2f} seconds\n")

    # Test concurrent prompt method
    print("Testing concurrent prompt (fastprompt):")
    start_time = time.time()
    fast_prompt_result, fast_images = prompt_instance(use_fast=True)  # Concurrent processing
    end_time = time.time()
    print(f"Concurrent prompt output:\n{fast_prompt_result}")
    print(f"Images: {fast_images}")
    print(f"Time taken (concurrent): {end_time - start_time:.2f} seconds")