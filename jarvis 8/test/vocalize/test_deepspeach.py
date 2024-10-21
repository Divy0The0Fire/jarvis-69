import deepspeech
import numpy as np
import pyaudio

model = deepspeech.Model('deepspeech-model.pbmm')
mic = pyaudio.PyAudio()

stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True)
stream.start_stream()

print("Listening...")

while True:
    audio_data = stream.read(1024)
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    text = model.stt(audio_array)
    print(text)
