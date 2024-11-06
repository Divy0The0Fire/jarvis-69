import vosk
import pyaudio
from time import time as t

# Set up the model
model = vosk.Model(lang="en-us")

RATE = 16000

# Initialize recognizer and audio stream
recognizer = vosk.KaldiRecognizer(model, RATE)
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True)
stream.start_stream()

print("Listening...")

while True:
    data = stream.read(4000, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        C = t()
        result = recognizer.Result()
        print(result)
        print(t() - C)

# No, yes, it.