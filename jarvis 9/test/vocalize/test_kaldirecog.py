import speech_recognition as sr
import pyaudio

def live_speech_to_text():
    # Initialize recognizer
    r = sr.Recognizer()

    # Set up microphone
    mic = sr.Microphone()

    print("Listening... Speak now!")

    with mic as source:
        # Adjust for ambient noise
        r.adjust_for_ambient_noise(source)

        while True:
            try:
                # Listen for speech
                audio = r.listen(source)

                # Recognize speech using Google Speech Recognition
                text = r.recognize_google(audio)

                print("You said:", text)

                # Check if user wants to stop
                if "stop listening" in text.lower():
                    print("Stopping...")
                    break

            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))

if __name__ == "__main__":
    live_speech_to_text()

