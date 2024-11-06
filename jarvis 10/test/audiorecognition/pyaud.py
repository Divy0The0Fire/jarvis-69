import pyaudio
import numpy as np
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
    rms = np.sqrt(np.mean(np.array(data, dtype=float)**2))
    if rms > 0:
        db = 20 * np.log10(rms)
    else:
        db = -float('inf')
    return max(db, 0)  # Ensure non-negative value

def audio_monitor():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    progress = Progress(BarColumn(bar_width=None), "[progress.percentage]{task.percentage:>3.0f}%")
    task = progress.add_task("", total=100)

    with Live(Panel("Starting audio monitoring...", title="Audio Monitor", border_style="blue"), refresh_per_second=10) as live:
        try:
            while True:
                data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
                db = calculate_db(data)
                
                # Update progress bar
                progress.update(task, completed=min(db, 100))
                
                # Create and update panel
                panel = Panel(
                    f"{progress}\nDecibels: {db:.2f} dB",
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
