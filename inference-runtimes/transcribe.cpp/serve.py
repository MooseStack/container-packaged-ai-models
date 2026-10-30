#!/usr/bin/env python3
"""OpenAI-compatible ASR server for transcribe.cpp GGUF models."""
from __future__ import annotations

import array
import asyncio
import io
import os
import wave
from pathlib import Path

import transcribe_cpp
import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

MODEL_DIR = Path(os.getenv("MODEL_PATH", "/models"))
MODEL_NAME = os.getenv("MODEL_NAME", "default")
BACKEND = os.getenv("TRANSCRIBE_BACKEND", "cpu")


def resolve_model_path() -> Path:
    explicit = os.getenv("MODEL_FILE", "").strip()
    if explicit:
        path = Path(explicit)
        return path if path.is_absolute() else MODEL_DIR / path
    if MODEL_DIR.is_file():
        return MODEL_DIR
    ggufs = sorted(MODEL_DIR.glob("*.gguf"))
    if not ggufs:
        raise FileNotFoundError(f"No .gguf model found under {MODEL_DIR}")
    return next(
        (p for p in ggufs if p.name.endswith(("-Q8_0.gguf", ".q8_0.gguf"))),
        ggufs[0],
    )


def wav_to_pcm(data: bytes) -> array.array:
    """Decode 16-bit PCM WAV → 16 kHz mono float32 (what transcribe.cpp expects)."""
    with wave.open(io.BytesIO(data), "rb") as wav:
        channels, width, rate, n = (
            wav.getnchannels(),
            wav.getsampwidth(),
            wav.getframerate(),
            wav.getnframes(),
        )
        frames = wav.readframes(n)

    if width != 2:
        raise ValueError(f"expected 16-bit PCM WAV, got {width * 8}-bit")
    if rate != 16000:
        raise ValueError(f"expected 16 kHz WAV, got {rate} Hz")

    pcm16 = array.array("h")
    pcm16.frombytes(frames)
    if channels > 1:
        frames_n = len(pcm16) // channels
        pcm16 = array.array(
            "h",
            (sum(pcm16[i * channels + c] for c in range(channels)) // channels for i in range(frames_n)),
        )
    return array.array("f", (s / 32768.0 for s in pcm16))


MODEL_PATH = resolve_model_path()
asr = transcribe_cpp.Model(str(MODEL_PATH), backend=BACKEND)
app = FastAPI(title="transcribe.cpp")


@app.get("/health")
@app.get("/v1/models")
def list_models():
    return {"object": "list", "data": [{"id": MODEL_NAME, "object": "model"}]}


@app.post("/v1/audio/transcriptions")
async def transcribe(
    file: UploadFile = File(...),
    language: str | None = Form(None),
    response_format: str = Form("json"),
):
    try:
        pcm = wav_to_pcm(await file.read())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Inference is sync/native; keep the event loop free.
    result = await asyncio.to_thread(transcribe_cpp.transcribe, asr, pcm, language=language)
    text = (result.text or "").strip()
    if response_format == "text":
        return PlainTextResponse(text)
    return {"text": text}


if __name__ == "__main__":
    host, port = os.getenv("HOST", "0.0.0.0"), int(os.getenv("PORT", "8080"))
    print(
        f"http://{host}:{port} model={MODEL_NAME} file={MODEL_PATH} "
        f"backend={BACKEND} native={transcribe_cpp.native_version()}",
        flush=True,
    )
    uvicorn.run(app, host=host, port=port, log_level="info")
