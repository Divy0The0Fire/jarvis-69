# pip install pocketsphinx
from pocketsphinx import LiveSpeech
for phrase in LiveSpeech():
    print(phrase)