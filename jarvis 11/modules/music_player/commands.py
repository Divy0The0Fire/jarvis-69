from .main import MusicPlayer
from typing import Optional

class MusicCommands:
    def __init__(self):
        self.player = MusicPlayer()
        
    def play_music(self, song_name: str) -> str:
        """Download and play a song by name"""
        return self.player.play(song_name)
    
    def pause_music(self) -> str:
        """Pause current track"""
        return self.player.pause()
    
    def stop_music(self) -> str:
        """Stop current track"""
        return self.player.stop()
    
    def set_music_volume(self, volume: float) -> str:
        """Set music volume (0-100)"""
        return self.player.set_volume(volume / 100)
    
    def list_music(self) -> str:
        """List all downloaded music tracks"""
        tracks = self.player.get_playlist()
        if not tracks:
            return "No music files found"
        return "Downloaded tracks:\n" + "\n".join(f"- {track}" for track in tracks)
    
    def music_status(self) -> str:
        """Get current music player status"""
        return self.player.get_status()
