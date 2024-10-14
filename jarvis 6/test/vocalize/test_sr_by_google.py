#!pip install SpeechRecognition
import speech_recognition as sr
from rich import print
from os import environ

environ["TF_ENABLE_ONEDNN_OPTS"]="0"

# Initialize recognizer
recognizer = sr.Recognizer()
# recognizer.energy_threshold = 300  # minimum audio energy to consider for recording
# recognizer.dynamic_energy_threshold = True
# recognizer.dynamic_energy_adjustment_damping = 0.15
# recognizer.dynamic_energy_ratio = 1.5
# recognizer.pause_threshold = 0.8  # seconds of non-speaking audio before a phrase is considered complete
# recognizer.operation_timeout = None  # seconds after an internal operation (e.g., an API request) starts before it times out, or ``None`` for no timeout
# recognizer.phrase_threshold = 0.3  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
# recognizer.non_speaking_duration = 0.5  # seconds of non-speaking audio to keep on both sides of the recording

def Listen() -> str|None:
    # Use the default microphone as the source
    with sr.Microphone(chunk_size=12288, sample_rate=44100) as source:
        print("listening ... ")
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, 1)

        # Listen to the user's input
        audio_data = recognizer.listen(source)
        print("i have heard enough")
        try:
            # print(f"{audio_data.get_raw_data()} ...")
            # Recognize speech using Google Speech Recognition
            text = recognizer.recognize_google(audio_data, language="en-In")
            # text = recognizer.recognize_google(audio_data)
            print(text)
            return text

        except sr.UnknownValueError:
            print("Could not understand the audio.")
            return Listen()

        except sr.RequestError as e:
            print(f"Error: {e}")
            return Listen()

if __name__=="__main__":
    while 1:
        Listen()