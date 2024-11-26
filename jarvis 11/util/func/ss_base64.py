import pyautogui
import base64
from io import BytesIO
from typing import Tuple

X8K = (7680, 4320)
X4K = (3840, 2160)
X2K = (2560, 1440)
X1080P = (1920, 1080)
X720P = (1280, 720)
X540P = (960, 540)
X360P = (640, 360)
X180P = (320, 180)
X144P = (256, 144)


def screenshot(size: Tuple[int, int] = X4K):
    # Capture the screenshot
    screenshot = pyautogui.screenshot()

    # Resize to 1920x1080 if not already (for consistency)
    screenshot = screenshot.resize(size)

    # Save to a BytesIO object
    buffered = BytesIO()
    screenshot.save(buffered, format="PNG")

    # Encode to Base64
    encoded_string = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Create the full Data URL
    data_url = f"data:image/png;base64,{encoded_string}"

    return data_url

if __name__ == "__main__":
    # Output the Data URL
    print(screenshot())

