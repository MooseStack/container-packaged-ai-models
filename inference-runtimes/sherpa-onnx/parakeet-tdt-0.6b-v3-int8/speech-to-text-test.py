#!/usr/bin/env python3
"""Offline ASR test client for Parakeet TDT (POST /v1/audio/transcriptions).

Parakeet is offline-only and rejects StreamingRecognize / realtime WebSocket
requests. Record from the mic until Ctrl+C, or pass an existing WAV file.
"""

import io
import json
import os
import sys
import wave
from contextlib import contextmanager
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pyaudio

# --- Configuration ---
BASE_URL = os.getenv("SHERPA_ONNX_URL", "http://127.0.0.1:8080").rstrip("/")
API_KEY = os.getenv("SHERPA_ONNX_API_KEY")
TRANSCRIPTIONS_URL = f"{BASE_URL}/v1/audio/transcriptions"

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SAMPLE_WIDTH = 2


@contextmanager
def suppress_alsa_output():
    saved_stderr = os.dup(2)
    null_device = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(null_device, 2)
        yield
    finally:
        os.dup2(saved_stderr, 2)
        os.close(null_device)
        os.close(saved_stderr)


def frames_to_wav(frames: list[bytes]) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(SAMPLE_WIDTH)
        wav_file.setframerate(RATE)
        wav_file.writeframes(b"".join(frames))
    return buffer.getvalue()


def record_microphone() -> bytes:
    with suppress_alsa_output():
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

    print("\n🎤 Recording... Press Ctrl+C to stop and transcribe.\n", flush=True)
    frames: list[bytes] = []
    try:
        while True:
            frames.append(stream.read(CHUNK))
    except KeyboardInterrupt:
        print("\n⏹ Stopping recording and sending audio...", flush=True)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

    if not frames:
        raise RuntimeError("No audio was recorded.")
    return frames_to_wav(frames)


def load_wav(path: str) -> bytes:
    with open(path, "rb") as handle:
        return handle.read()


def transcribe(wav_bytes: bytes, filename: str = "recording.wav") -> dict | str:
    boundary = "----sherpaOnnxBoundary7f3a9c"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: audio/wav\r\n\r\n"
    ).encode() + wav_bytes + (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="model"\r\n\r\n'
        f"default\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="response_format"\r\n\r\n'
        f"verbose_json\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="language"\r\n\r\n'
        f"en\r\n"
        f"--{boundary}--\r\n"
    ).encode()

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    request = Request(TRANSCRIPTIONS_URL, data=body, headers=headers, method="POST")
    with urlopen(request) as response:
        payload = response.read().decode()
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type or payload.lstrip().startswith("{"):
            return json.loads(payload)
        return payload


def main() -> int:
    if len(sys.argv) > 1:
        wav_path = sys.argv[1]
        print(f"📂 Transcribing {wav_path}...", flush=True)
        wav_bytes = load_wav(wav_path)
        filename = os.path.basename(wav_path)
    else:
        wav_bytes = record_microphone()
        filename = "recording.wav"

    try:
        result = transcribe(wav_bytes, filename=filename)
    except HTTPError as error:
        detail = error.read().decode(errors="replace")
        print(f"❌ Server error ({error.code}): {detail}")
        return 1
    except (URLError, OSError, RuntimeError) as error:
        print(f"❌ Could not transcribe audio: {error}")
        return 1

    if isinstance(result, dict):
        text = result.get("text", "")
        print(f"\n📝 {text}", flush=True)
        if result.get("words"):
            print(f"\n⏱ {len(result['words'])} words with timestamps", flush=True)
    else:
        print(f"\n📝 {result}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
