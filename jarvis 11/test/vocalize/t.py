import requests
import soundfile as sf
import io
from pydub import AudioSegment
from time import time as t
# Read the WAV file
audio = AudioSegment.from_wav("recorded_audio.wav")

# Convert to FLAC
flac_buffer = io.BytesIO()
audio.export(flac_buffer, format="flac")
flac_data = flac_buffer.getvalue()

sess = requests.Session()
C = t()
# Make the POST request
response = sess.post(
    "http://www.google.com/speech-api/v2/recognize?client=chromium&lang=en-US&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw&pFilter=0",
    data=flac_data,
    headers={"Content-Type": "audio/x-flac; rate=16000"}
)

print(response.text)
print(t() - C)
C = t()
# Make the POST request
response = sess.post(
    "http://www.google.com/speech-api/v2/recognize?client=chromium&lang=en-US&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw&pFilter=0",
    data=flac_data,
    headers={"Content-Type": "audio/x-flac; rate=16000"}
)

print(response.text)
print(t() - C)
