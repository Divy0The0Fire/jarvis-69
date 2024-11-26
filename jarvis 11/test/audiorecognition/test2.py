import sounddevice as sd
import numpy as np
import wave

# Audio settings
duration = 10  # Recording duration in seconds
sample_rate = 44100  # Sample rate (Hz)
channels = 1  # Mono for microphone

# Initialize an empty array to store audio data
audio_data = np.array([], dtype=np.float32)

# Callback function to handle audio data
def audio_callback(indata, frames, time, status):
    global audio_data
    if status:
        print(status)
    audio_data = np.append(audio_data, indata.copy())

# Start the audio stream
with sd.InputStream(callback=audio_callback, channels=channels, samplerate=sample_rate):
    print(f"Recording microphone audio for {duration} seconds...")
    sd.sleep(int(duration * 1000))

# Reshape the audio data
audio_data = audio_data.reshape(-1, channels)

# Save the recorded audio to a WAV file
output_file = "microphone_audio.wav"
with wave.open(output_file, 'wb') as wf:
    wf.setnchannels(channels)
    wf.setsampwidth(2)  # 16-bit audio
    wf.setframerate(sample_rate)
    wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

print(f"Audio saved to {output_file}")
