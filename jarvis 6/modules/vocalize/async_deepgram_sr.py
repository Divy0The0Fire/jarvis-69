import asyncio
import os
import sys
import logging

try:
    from modules.sqlqueue import SqlQueue
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(__file__) + "/../../")
    from modules.sqlqueue import SqlQueue


from dotenv import load_dotenv

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone
)
from pythonjsonlogger import jsonlogger
from rich.logging import RichHandler
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", None)
DEEPGRAM_MODEL = os.getenv("DEEPGRAM_MODEL", "nova-2")
SPEECHRECOGNITION_LANGUAGE = os.getenv("SPEECHRECOGNITION_LANGUAGE", "en-US")
TMP_DIR = os.getenv("TMP_DIR", "/tmp")
DATA_DIR = os.getenv("DATA_DIR")

logger = logging.getLogger(__file__.split("/")[-1])
logger.setLevel(logging.INFO)  # Set default log level
json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(name)s %(funcName)s')
rich_handler = RichHandler()
logger.addHandler(rich_handler)
LOG_FILE = os.path.join(DATA_DIR, "log", "async_deepgram_sr.log")
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(json_formatter)
logger.addHandler(file_handler)

if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

Queue = SqlQueue(os.path.join(TMP_DIR, "async_deepgram_sr.queue.db"))

if DEEPGRAM_API_KEY is None:
    logger.error("Please set the DEEPGRAM_API_KEY environment variable")
    raise Exception("Please set the DEEPGRAM_API_KEY environment variable")


class TranscriptCollector:
    def __init__(self):
        self.reset()

    def reset(self):
        self.transcript_parts = []

    def add_part(self, part):
        self.transcript_parts.append(part)

    def get_full_transcript(self):
        return ' '.join(self.transcript_parts)

transcript_collector = TranscriptCollector()







async def get_transcript():
    try:
        config = DeepgramClientOptions(api_key=DEEPGRAM_API_KEY, options={"keepalive": "true"})
        deepgram: DeepgramClient = DeepgramClient(DEEPGRAM_API_KEY, config)

        dg_connection = deepgram.listen.asynclive.v("1")

        async def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript

            # print (f"{result = }")
            
            if not result.speech_final:
                transcript_collector.add_part(sentence)
            else:
                # This is the final part of the current sentence
                transcript_collector.add_part(sentence)
                full_sentence = transcript_collector.get_full_transcript()
                # print(f"speaker: {full_sentence}")
                string = full_sentence.strip()
                if string:
                    Queue.put(string)
                # Reset the collector for the next sentence
                transcript_collector.reset()

        async def on_error(self, error, **kwargs):
            print(f"\n\n{error}\n\n")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)


        options = LiveOptions(
            model=DEEPGRAM_MODEL,
            punctuate=True,
            language=SPEECHRECOGNITION_LANGUAGE,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=True
        )

        await dg_connection.start(options)
        logger.info("connected")

        # Open a microphone stream on the default input device
        microphone = Microphone(dg_connection.send)

        # start microphone
        microphone.start()
        logger.info("microphone started")

        while True:
            if not microphone.is_active():
                logger.info("microphone stopped")
                break
            await asyncio.sleep(1)

        # Wait for the microphone to close
        microphone.finish()
        logger.info("microphone finished")
        # Indicate that we've finished
        dg_connection.finish()
        logger.info("connection finished")

    except Exception as e:
        logger.error(e)
        print(f"Could not open socket: {e}")
        if f"{e}".endswith("HTTP 401"):
            logger.error("Invalid API Key Check your DEEPGRAM_API_KEY environment variable")
            raise Exception("Invalid API Key Check your DEEPGRAM_API_KEY environment variable")
        return

if __name__ == "__main__":
    asyncio.run(get_transcript())