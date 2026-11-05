"""Microphone helpers shared by the manual audio smoke clients."""

import io
import os
import threading
import wave
from contextlib import contextmanager

CHUNK = 1024
RATE = 16000


@contextmanager
def microphone():
    try:
        import pyaudio
    except ImportError as error:
        raise RuntimeError("Microphone input requires pyaudio: python3 -m pip install pyaudio") from error

    # PortAudio can print ALSA device warnings while opening the default input.
    saved_stderr = os.dup(2)
    null_device = os.open(os.devnull, os.O_WRONLY)
    audio = None
    try:
        os.dup2(null_device, 2)
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
    except Exception:
        if audio is not None:
            audio.terminate()
        raise
    finally:
        os.dup2(saved_stderr, 2)
        os.close(null_device)
        os.close(saved_stderr)

    try:
        yield stream
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()


def record_wav():
    frames = []
    stop_requested = threading.Event()

    def wait_for_enter():
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass
        stop_requested.set()

    stopper = threading.Thread(target=wait_for_enter, daemon=True)
    stopper.start()
    with microphone() as stream:
        print("Recording... Press Enter to stop and transcribe (Ctrl+C also works).", flush=True)
        try:
            while not stop_requested.is_set():
                frames.append(stream.read(CHUNK))
        except KeyboardInterrupt:
            stop_requested.set()

    if not frames:
        raise RuntimeError("No audio was recorded.")

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(RATE)
        wav_file.writeframes(b"".join(frames))
    return buffer.getvalue()
