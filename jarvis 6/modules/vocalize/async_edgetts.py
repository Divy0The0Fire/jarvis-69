# https://gist.github.com/BettyJJ/17cbaa1de96235a7f5773b8690a20462
# voice output, EDGE TTS
import edge_tts
import io
import pygame
from rich import print

async def fetchAudio(text, assistantVoice="en-US-EricNeural", pitch='+0Hz', rate='+0%') -> bytes:
    """
    Fetch audio from TTS service

    Args:
        text (str): text to convert
        AssistantVoice (str, optional): Voice. Defaults to "en-US-EricNeural".
        pitch (str, optional): pitch. Defaults to '0Hz'. [-100, +100]Hz
        rate (str, optional): rate. Defaults to '0%'. [-100, +100]%
    """
    try:
        communicate = edge_tts.Communicate(text, assistantVoice, pitch=pitch, rate=rate)
        audioBytes = b""
        async for element in communicate.stream():
            if element["type"] == 'audio':
                audioBytes += element["data"]
        return audioBytes
    except Exception as e:
        print(e)
        return b""


async def textToSpeechBytes(text: str, assistantVoice="en-US-EricNeural") -> bytes:
    return await fetchAudio(text, assistantVoice)


class AudioPlayer:
    def __init__(self):
        # Initialize the pygame mixer only once
        pygame.mixer.init()

        self.channel = None  # Channel for the sound
        self.sound = None  # Placeholder for sound object

    def play(self, audio_bytes: bytes) -> None:
        # Convert bytes to a file-like object
        audio_file = io.BytesIO(audio_bytes)
        
        # Load the audio from the file-like object
        self.sound = pygame.mixer.Sound(audio_file)

        # Stop any currently playing sound before playing new audio
        if self.channel and self.channel.get_busy():
            self.channel.stop()

        # Play the new audio
        self.channel = self.sound.play()
    
    def stop(self) -> None:
        if self.channel and self.channel.get_busy():
            self.channel.stop()  # Stop the sound if it's playing
        else:
            print("No audio is currently playing.")

    def pause(self) -> None:
        if self.channel and self.channel.get_busy():
            self.channel.pause()  # Pause the sound if it's playing
    
    def unpause(self) -> None:
        if self.channel and self.channel.get_busy():
            self.channel.unpause()  # Unpause the sound if it's paused

    
    def setVolume(self, volume: float) -> None:
        """
        Set the volume of the sound

        Args:
            volume (float): Volume level between 0 and 1
            
        """
        if self.channel:
            self.channel.set_volume(volume)


    def getVolume(self) -> float:
        if self.channel:
            return self.channel.get_volume()
        return 0

    def getDuration(self) -> float:
        if self.sound:
            return self.sound.get_length()
        return 0

    def getDurationInSeconds(self) -> float:
        if self.sound:
            return self.sound.get_length() / 1000
        return 0
    
    def getDurationInMinutes(self) -> float:
        if self.sound:
            return self.sound.get_length() / 1000 / 60
        return 0
    
    def isPlaying(self) -> bool:
        if self.channel:
            return self.channel.get_busy()  # Check if the sound is playing
        return False


if __name__ == "__main__":
    from time import sleep
    import asyncio
    text = "Hello, how are you?"
    audioBytes = asyncio.run(textToSpeechBytes(text))
    player = AudioPlayer()
    player.play(audioBytes)
    sleep(1)
    player.pause()
    sleep(1)
    player.setVolume(1)
    player.unpause()
    sleep(1)
    player.stop()