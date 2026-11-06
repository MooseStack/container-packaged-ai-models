#!/usr/bin/env python3
"""Smoke-test an offline OpenAI-style audio transcription endpoint."""

import argparse
import io
import json
import os
import time
import wave
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from _audio import record_wav

BATCH_SECONDS = 5


def wav_batches(wav_bytes, seconds=BATCH_SECONDS):
    """Yield valid WAV files containing at most ``seconds`` of audio each."""
    with wave.open(io.BytesIO(wav_bytes), "rb") as source:
        frames_per_batch = max(1, int(source.getframerate() * seconds))
        params = source.getparams()
        while True:
            frames = source.readframes(frames_per_batch)
            if not frames:
                return

            batch = io.BytesIO()
            with wave.open(batch, "wb") as destination:
                destination.setnchannels(params.nchannels)
                destination.setsampwidth(params.sampwidth)
                destination.setframerate(params.framerate)
                destination.setcomptype(params.comptype, params.compname)
                destination.writeframes(frames)
            yield batch.getvalue()


def multipart(wav_bytes, filename, model, response_format):
    boundary = f"----audioTest{uuid4().hex}"
    fields = {"model": model, "response_format": response_format, "language": "en"}
    body = bytearray()
    body.extend(
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: audio/wav\r\n\r\n".encode()
    )
    body.extend(wav_bytes)
    body.extend(b"\r\n")
    for name, value in fields.items():
        body.extend(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n".encode()
        )
    body.extend(f"--{boundary}--\r\n".encode())
    return boundary, bytes(body)


def transcribe(wav_bytes, filename, args, url):
    boundary, body = multipart(
        wav_bytes, filename, args.model, args.response_format
    )
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    if args.api_key:
        headers["Authorization"] = f"Bearer {args.api_key}"
    request = Request(
        f"{url}/v1/audio/transcriptions",
        data=body,
        headers=headers,
        method="POST",
    )
    with urlopen(request) as response:
        payload = response.read().decode()
        content_type = response.headers.get("Content-Type", "")
    return json.loads(payload) if "application/json" in content_type or payload.lstrip().startswith("{") else payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.getenv("AUDIO_TRANSCRIPTION_URL", "http://127.0.0.1:8080"), help="Server base URL")
    parser.add_argument("--api-key", default=os.getenv("AUDIO_TRANSCRIPTION_API_KEY"), help="Bearer token")
    parser.add_argument("--model", default=os.getenv("AUDIO_TRANSCRIPTION_MODEL", "default"), help="Model identifier")
    parser.add_argument("--response-format", default=os.getenv("AUDIO_TRANSCRIPTION_RESPONSE_FORMAT", "json"), help="Response format")
    parser.add_argument("wav", nargs="?", type=Path, help="16 kHz mono 16-bit PCM WAV; record from microphone if omitted")
    args = parser.parse_args()

    url = args.url.rstrip("/")
    try:
        wav_bytes = args.wav.read_bytes() if args.wav else record_wav()
        filename = args.wav.name if args.wav else "recording.wav"
        results = []
        for batch_number, batch in enumerate(wav_batches(wav_bytes), start=1):
            print(f"Transcribing 5-second batch {batch_number}...", flush=True)
            started = time.monotonic()
            result = transcribe(batch, filename, args, url)
            results.append(result)
            batch_text = result.get("text", "") if isinstance(result, dict) else str(result)
            elapsed = time.monotonic() - started
            print(
                f"Batch {batch_number} completed in {elapsed:.1f}s: "
                f"{batch_text.strip() or '[no transcription]'}",
                flush=True,
            )
    except HTTPError as error:
        print(f"Server error ({error.code}): {error.read().decode(errors='replace')}")
        return 1
    except (URLError, OSError, RuntimeError, ValueError, wave.Error) as error:
        print(f"Could not transcribe audio: {error}")
        return 1

    if all(isinstance(result, dict) for result in results):
        text = " ".join(result.get("text", "").strip() for result in results).strip()
        print(text or json.dumps(results, indent=2))
        word_count = sum(len(result.get("words", [])) for result in results)
        if word_count:
            print(f"{word_count} words with timestamps")
    else:
        print(" ".join(str(result).strip() for result in results).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
