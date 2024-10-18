# pip install -U realtimetts[all]
from RealtimeTTS import TextToAudioStream, CoquiEngine, AzureEngine, ElevenlabsEngine
from time import time as t


# IF you are reading this please don't run this. it will burn you pc. :( 


if __name__ == "__main__":
    engine = CoquiEngine() # replace with your TTS engine
    stream = TextToAudioStream(engine)
    print("feeding")
    C = t()
    stream.feed("Hello world! How are you today?")
    print("playing")
    print(t()-C)
    stream.play_async()
    print("done")