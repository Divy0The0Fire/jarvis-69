import pygame
import os
from typing import Optional, List, Dict, Any
from pathlib import Path
import threading
import time
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yt_song_downloader import download_song

class MusicPlayer:
    def __init__(self, music_dir: str = None, default_volume: float = 0.1):
        """Initialize the music player with the specified music directory"""
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Set up music directory
        if music_dir is None:
            music_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
        self.music_dir = Path(music_dir)
        os.makedirs(self.music_dir, exist_ok=True)
        
        # Player state
        self.current_track: Optional[str] = None
        self.is_playing = False
        self.is_paused = False
        self.volume = default_volume
        self.progress = 0.0
        self.duration = 0
        self.supported_formats = ('.mp3', '.wav', '.ogg')
        self.is_looping = False
        
        # Set initial volume
        pygame.mixer.music.set_volume(self.volume)
        
        # Start progress update thread
        self._progress_thread = threading.Thread(target=self._update_progress, daemon=True)
        self._progress_thread.start()
        
        # Set up end event handler for looping
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)  # Use unique event ID
        self._event_thread = threading.Thread(target=self._handle_events, daemon=True)
        self._event_thread.start()
    
    def __del__(self):
        """Cleanup pygame on deletion"""
        try:
            pygame.mixer.quit()
            pygame.quit()
        except:
            pass
    
    def _update_progress(self):
        """Update playback progress in a background thread"""
        while True:
            if self.is_playing and not self.is_paused and self.duration > 0:
                pos = pygame.mixer.music.get_pos()
                if pos > 0:  # Only update if we have a valid position
                    self.progress = pos / 1000
            time.sleep(0.1)
    
    def _handle_events(self):
        """Handle pygame events for music end"""
        clock = pygame.time.Clock()
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.USEREVENT + 1:  # Match our unique event ID
                        if self.is_looping and self.current_track:
                            # Restart the same track
                            pygame.mixer.music.play()
                        else:
                            # Stop playback
                            self.stop()
                clock.tick(10)  # Limit to 10 FPS to reduce CPU usage
        except Exception as e:
            print(f"Event handler error: {str(e)}")
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds into MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def play(self, song_name: Optional[str] = None) -> str:
        """Play a song by name or URL, or resume current track"""
        try:
            if song_name:
                print(f"Downloading: {song_name}")
                
                # Download the song
                result = download_song(song_name, self.music_dir)
                
                if not result['success']:
                    return f"Failed to download: {result['error']}"
                
                # Load and play the song
                pygame.mixer.music.load(result['file_path'])
                pygame.mixer.music.play()
                
                self.current_track = result['title']
                self.is_playing = True
                self.is_paused = False
                self.duration = result['duration'] or 0
                self.progress = 0
                
                return f"▶ Playing: {self.current_track}"
            
            elif self.current_track and self.is_paused:
                return self.unpause()
            
            return "No track selected"
            
        except Exception as e:
            return f"Error playing track: {str(e)}"
    
    def pause(self) -> str:
        """Pause the current track"""
        if self.current_track:  # Check if we have a track loaded
            pygame.mixer.music.pause()
            self.is_paused = True
            return f"⏸ Paused: {self.current_track}"
        return "No track is playing"

    def unpause(self) -> str:
        """Unpause the current track"""
        if self.current_track:  # Check if we have a track loaded
            pygame.mixer.music.unpause()
            self.is_paused = False
            return f"▶ Resumed: {self.current_track}"
        return "No track is paused"
    
    def stop(self) -> str:
        """Stop the current track"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_track = None
        self.progress = 0
        return "⏹ Stopped playback"
    
    def set_volume(self, volume: float) -> str:
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        return f"🔊 Volume: {int(self.volume * 100)}%"
    
    def toggle_loop(self) -> str:
        """Toggle loop mode for current track"""
        self.is_looping = not self.is_looping
        return f"🔁 Loop {'enabled' if self.is_looping else 'disabled'}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current player status"""
        status = {
            "state": "stopped",
            "track": None,
            "progress": "00:00",
            "duration": "00:00",
            "volume": int(self.volume * 100),
            "is_playing": False,
            "is_paused": False,
            "is_looping": self.is_looping
        }
        
        if self.current_track:
            if self.is_playing:
                if self.is_paused:
                    status["state"] = "⏸ Paused"
                else:
                    status["state"] = "▶ Playing"
            status["track"] = self.current_track
            status["progress"] = self._format_time(self.progress)
            status["duration"] = self._format_time(self.duration)
            status["is_playing"] = self.is_playing
            status["is_paused"] = self.is_paused
            
            # Calculate progress percentage
            if self.duration > 0:
                status["progress_percent"] = int((self.progress / self.duration) * 100)
            else:
                status["progress_percent"] = 0
            
            # Create a progress bar
            bar_length = 20
            filled = int(bar_length * (status["progress_percent"] / 100))
            status["progress_bar"] = f"[{'=' * filled}{'-' * (bar_length - filled)}]"
        
        return status

    def display_status(self) -> str:
        """Get a formatted string of the current status"""
        status = self.get_status()
        
        if not status["track"]:
            return "No track loaded"
        
        loop_status = "🔁 Loop On" if status["is_looping"] else ""
        return (
            f"{status['state']}: {status['track']} {loop_status}\n"
            f"Time: {status['progress']} / {status['duration']} {status['progress_bar']}\n"
            f"Volume: {status['volume']}%"
        )
    
    def get_playlist(self) -> List[str]:
        """Get list of downloaded songs"""
        music_files = []
        for file in self.music_dir.glob("**/*"):
            if file.suffix.lower() in self.supported_formats:
                music_files.append(file.name)
        return music_files

def run_interactive_player():
    """Run the music player in interactive mode"""
    player = MusicPlayer()
    
    while True:
        try:
            command = input("\nEnter command (play/pause/unpause/stop/loop/volume/list/status/quit): ").strip().lower()
            
            if command == 'quit' or command == 'q':
                print("Stopping playback...")
                player.stop()
                break
            
            elif command.startswith('play') or command.startswith('p '):
                # Extract song name if provided
                parts = command.split(' ', 1)
                song_name = parts[1] if len(parts) > 1 else None
                print(player.play(song_name))
            
            elif command == 'pause' or command == 'pa':
                print(player.pause())
            
            elif command == 'unpause' or command == 'resume' or command == 'r' or command == 'u':
                print(player.unpause())
            
            elif command == 'stop' or command == 'st':
                print(player.stop())
            
            elif command == 'loop' or command == 'lo':
                print(player.toggle_loop())
            
            elif command.startswith('volume') or command.startswith('v '):
                try:
                    # Extract volume level (0-100)
                    vol = float(command.split()[1]) / 100
                    print(player.set_volume(vol))
                except (IndexError, ValueError):
                    print("Usage: volume <0-100>")
            
            elif command == 'list' or command == 'ls':
                playlist = player.get_playlist()
                if playlist:
                    print("\nAvailable songs:")
                    for i, song in enumerate(playlist, 1):
                        print(f"{i}. {song}")
                else:
                    print("No songs downloaded yet")
            
            elif command == 'status' or command == 'stat':
                print(player.display_status())
            
            else:
                print("Commands:")
                print("  play/p [song]  - Play a song (or resume current)")
                print("  pause/pa      - Pause current song")
                print("  unpause/r/u   - Resume paused song")
                print("  stop/st       - Stop playback")
                print("  loop/lo       - Toggle loop mode")
                print("  volume/v <0-100> - Set volume")
                print("  list/ls       - Show downloaded songs")
                print("  status/stat   - Show player status")
                print("  quit/q        - Exit player")
                
        except KeyboardInterrupt:
            print("\nStopping playback...")
            player.stop()
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_interactive_player()