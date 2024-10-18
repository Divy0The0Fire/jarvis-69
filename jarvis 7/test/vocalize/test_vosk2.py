import vosk
import pyaudio

# Set up the model
model = vosk.Model(lang="en-us")

# Initialize recognizer and audio stream
recognizer = vosk.KaldiRecognizer(model, 16000)
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True)
stream.start_stream()

print("Listening...")

while True:
    data = stream.read(4000, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = recognizer.Result()
        print(result)


# No, yes, it.