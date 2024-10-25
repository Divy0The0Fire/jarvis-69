import numpy as np
import sounddevice as sd
import time

def calculate_audio_strength_and_db(indata):
    # Calculate RMS of the audio data
    rms = np.sqrt(np.mean(indata**2))
    
    # Convert RMS to decibels
    # We add a small value (1e-10) to avoid log(0)
    db = 20 * np.log10(rms + 1e-10)
    
    # Normalize for display purposes (0-100)
    strength = int(min(rms * 1000, 100))
    
    return strength, db

def display_audio_info(strength, db):
    bar_length = 50
    filled_length = int(strength / 2)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    percentage = strength if strength <= 100 else 100
    print(f'\rAudio strength: |{bar}| {percentage}% | {db:.2f} dB', end='', flush=True)

def live_audio_monitor(sample_rate=44100):
    try:
        with sd.InputStream(callback=lambda *args: None,
                            channels=1,
                            samplerate=sample_rate):
            print("Monitoring audio... Press Ctrl+C to stop.")
            while True:
                recorded = sd.rec(int(sample_rate * 0.1), samplerate=sample_rate, channels=1)
                sd.wait()
                strength, db = calculate_audio_strength_and_db(recorded)
                display_audio_info(strength, db)
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    live_audio_monitor()
