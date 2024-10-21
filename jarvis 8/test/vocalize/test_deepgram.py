import asyncio
import os

from dotenv import load_dotenv

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
from rich import print

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", None)
DEEPGRAM_MODEL = os.getenv("DEEPGRAM_MODEL", "nova-2")
SPEECHRECOGNITION_LANGUAGE = os.getenv("SPEECHRECOGNITION_LANGUAGE", "en-US")

if DEEPGRAM_API_KEY is None:
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
                print(f"speaker: {full_sentence}")
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

        # Open a microphone stream on the default input device
        microphone = Microphone(dg_connection.send)

        # start microphone
        microphone.start()

        while True:
            if not microphone.is_active():
                break
            await asyncio.sleep(1)

        # Wait for the microphone to close
        microphone.finish()

        # Indicate that we've finished
        dg_connection.finish()

        print("Finished")

    except Exception as e:
        print(f"Could not open socket: {e}")
        if f"{e}".endswith("HTTP 401"):
            raise Exception("Invalid API Key Check your DEEPGRAM_API_KEY environment variable")
        return

if __name__ == "__main__":
    asyncio.run(get_transcript())