#!pip install SpeechRecognition
import speech_recognition as sr
import threading
import queue
import os
import sys
import logging


from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger
from rich.logging import RichHandler

load_dotenv()

try:
    from modules.sqlqueue import SqlQueue
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(__file__) + "/../../")
    from modules.sqlqueue import SqlQueue

SPEECHRECOGNITION_LANGUAGE = os.getenv("SPEECHRECOGNITION_LANGUAGE", "en-US")
TMP_DIR = os.getenv("TMP_DIR", "/tmp")
DATA_DIR = os.getenv("DATA_DIR")

logger = logging.getLogger(__file__.split("/")[-1])
logger.setLevel(logging.INFO)  # Set default log level
json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(name)s %(funcName)s')
rich_handler = RichHandler()
logger.addHandler(rich_handler)
LOG_FILE = os.path.join(DATA_DIR, "log", "async_google_sr.log")
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(json_formatter)
logger.addHandler(file_handler)

if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)


# Initialize recognizer
recognizer = sr.Recognizer()

logger.info(f"Using language: {SPEECHRECOGNITION_LANGUAGE}")

# Create a queue to hold recognized text
text_queue = queue.Queue()

# Function to listen for audio in a separate thread
def listen():
    with sr.Microphone(chunk_size=12288, sample_rate=44100) as source:
        # print("Listening...")
        logger.info("Microphone listening...")
        recognizer.adjust_for_ambient_noise(source, 0.5)

        while True:
            try:
                # Listen to the user's input
                audio_data = recognizer.listen(source)
                # print("I have heard enough.")
                # Put the audio data in the queue for processing
                text_queue.put(audio_data)

            except sr.UnknownValueError:
                print("Could not understand the audio.")

            except sr.RequestError as e:
                logger.error(f"Error: {e}")
                print(f"Error: {e}")

# Function to process recognized text
def process_recognition():
    Queue = SqlQueue(os.path.join(TMP_DIR, f"async_google_sr.queue.db"))

    while True:
        # Get audio data from the queue
        audio_data = text_queue.get()
        if audio_data is None:
            break  # Exit if None is received

        try:
            # Recognize speech using Google Speech Recognition
            text = recognizer.recognize_google(audio_data, language=SPEECHRECOGNITION_LANGUAGE)
            # print(f"Recognized: {text}")
            Queue.put(text)

        except sr.UnknownValueError:
            print("Could not understand the audio.")
        except sr.RequestError as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")

# Main execution block
if __name__ == "__main__":
    # Start the listening thread
    listen_thread = threading.Thread(target=listen)
    listen_thread.daemon = True  # Ensure the thread exits when the main program does
    listen_thread.start()

    # Start the processing thread
    process_thread = threading.Thread(target=process_recognition)
    process_thread.daemon = True
    process_thread.start()

    # Wait for both threads to finish
    listen_thread.join()
    process_thread.join()