import os
import speech_recognition as sr
from dotenv import load_dotenv
import vosk
import pyaudio
import wave
from time import time
from pydub import AudioSegment
import io
import asyncio

load_dotenv()

# Remove the Groq client initialization
# client = Groq()

async def recognize_speech(audio_bytes, file_format="mp3", language="en-US"):
    # Convert MP3 to WAV if necessary
    if file_format.lower() == "mp3":
        audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
        wav_bytes = io.BytesIO()
        audio.export(wav_bytes, format="wav")
        audio_bytes = wav_bytes.getvalue()

    recognizer = sr.Recognizer()
    audio_data = sr.AudioData(audio_bytes, sample_rate=16000, sample_width=2)

    async def recognize_worker():
        try:
            return await asyncio.to_thread(recognizer.recognize_google, audio_data, language=language)
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"

    # Create 5 parallel recognition tasks
    tasks = [recognize_worker() for _ in range(1)]

    # Wait for the first task to complete
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    # Cancel the remaining tasks
    # for task in pending:
    #     task.cancel()

    # Get the result of the first completed task
    result = done.pop().result()

    return result

# Set up the model and audio parameters
model = vosk.Model(lang="en-us")
RATE = 16000
CHUNK = 4000

# Initialize recognizer and audio stream
recognizer = vosk.KaldiRecognizer(model, RATE)
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
stream.start_stream()

print("Listening...")

async def process_audio():
    audio_data = b""
    while True:
        data = await asyncio.to_thread(stream.read, CHUNK, exception_on_overflow=False)
        audio_data += data
        if recognizer.AcceptWaveform(data):
            start_time = time()
            
            # Convert audio data to MP3
            wav_audio = AudioSegment(
                audio_data,
                frame_rate=RATE,
                sample_width=mic.get_sample_size(pyaudio.paInt16),
                channels=1
            )
            mp3_buffer = io.BytesIO()
            wav_audio.export(mp3_buffer, format="mp3")
            mp3_data = mp3_buffer.getvalue()
            
            resultOG = recognizer.Result()
            print(resultOG)
            
            # Process the audio data using Google Speech Recognition
            result = await recognize_speech(mp3_data, file_format="mp3")
            
            print(result)
            print(f"Processing time: {time() - start_time:.2f} seconds")
            
            audio_data = b""  # Reset audio data for the next iteration

if __name__ == "__main__":
    try:
        asyncio.run(process_audio())
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()
