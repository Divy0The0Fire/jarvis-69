import os
import time
import wave
import pyaudio
from faster_whisper import WhisperModel

# Определяем константы
NEON_GREEN = '\033[32m'
RESET_COLOR = '\033[0m'

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
# Функция для записи аудио-фрагмента
def record_chunk(p, stream, file_path, chunk_length=1):
    """
    Записывает аудиофрагмент в файл.

    Args:
        p (pyaudio.PyAudio): Объект PyAudio.
        stream (pyaudio.Stream): Поток PyAudio.
        file_path (str): Путь к файлу, куда будет записан аудиофрагмент.
        chunk_length (int): Длина аудиофрагмента в секундах.

    Returns:
        None
    """

    frames = []

    for _ in range(0, int(16000 / 1024 * chunk_length)):
        data = stream.read(1024)
        frames.append(data)

    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_chunk(model, file_path):
    segments, info = model.transcribe(file_path, beam_size=7)
    transcription = ''.join(segment.text for segment in segments)
    return transcription

def main2():
    """
    Основная функция программы.
    """

    # Выбираем модель Whisper
    model = WhisperModel("tiny.en", device="cpu", compute_type="float32")

    # Инициализируем PyAudio
    p = pyaudio.PyAudio()

    # Открываем поток записи
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

    # Инициализируем пустую строку для накопления транскрипций
    accumulated_transcription = ""

    try:
        while True:
            # Записываем аудиофрагмент
            chunk_file = "temp_chunk.wav"
            record_chunk(p, stream, chunk_file)

            # Транскрибируем аудиофрагмент
            transcription = transcribe_chunk(model, chunk_file)
            print(NEON_GREEN + transcription + RESET_COLOR)

            # Удаляем временный файл
            os.remove(chunk_file)

            # Добавляем новую транскрипцию к накопленной транскрипции
            accumulated_transcription += transcription + " "

    except KeyboardInterrupt:
        print("Stopping...")

        # Записываем накопленную транскрипцию в лог-файл
        with open("log.txt", "w") as log_file:
            log_file.write(accumulated_transcription)

    finally:
        print("LOG" + accumulated_transcription)
        # Закрываем поток записи
        stream.stop_stream()
        stream.close()

        # Останавливаем PyAudio
        p.terminate()


if __name__ == "__main__":
    main2()