import pyaudio
import numpy as np
from pydub import AudioSegment
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

console = Console()

def calculate_db(data):
    # Convert the raw data to an AudioSegment
    audio_segment = AudioSegment(
        data.tobytes(), 
        frame_rate=RATE,
        sample_width=data.dtype.itemsize, 
        channels=CHANNELS
    )
    
    # Calculate dB
    db = audio_segment.dBFS
    return max(db, -60)  # Limit the lower bound to -60 dB for display purposes

def audio_monitor():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    progress = Progress(BarColumn(bar_width=None), "[progress.percentage]{task.percentage:>3.0f}%")
    task = progress.add_task("", total=60)  # 60 dB range for display

    with Live(Panel("Starting audio monitoring...", title="Audio Monitor", border_style="blue"), refresh_per_second=10) as live:
        try:
            while True:
                data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
                db = calculate_db(data)
                
                # Update progress bar (normalize -60 to 0 dB to 0-100%)
                normalized_db = (db + 60) / 60 * 100
                progress.update(task, completed=max(min(normalized_db, 100), 0))
                
                # Create and update panel
                panel = Panel(
                    f"{progress}\nDecibels: {db:.2f} dBFS",
                    title="Audio Monitor",
                    border_style="blue"
                )
                live.update(panel)

        except KeyboardInterrupt:
            console.print("\nStopped by user")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

if __name__ == "__main__":
    audio_monitor()
