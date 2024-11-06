from elevenlabs import ElevenLabs, VoiceSettings
from dotenv import load_dotenv
from rich import print

import os
load_dotenv()

client = ElevenLabs(api_key=os.environ["ELEVEN_API_KEY"])
resp = client.text_to_speech.convert(
    voice_id="pMsXgVXv3BLzUgSXRplE",
    optimize_streaming_latency="0",
    output_format="mp3_22050_32",
    text="hi how",
    voice_settings=VoiceSettings(
        stability=0.1,
        similarity_boost=0.3,
        style=0.2,
    ),
)


print(resp)

for result in resp:
    print(result)