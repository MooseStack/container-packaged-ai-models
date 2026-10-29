#!/usr/bin/env python3
"""Minimal OpenAI-compatible ASR server for sherpa-onnx offline transducers."""
import io, json, os, re, wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import numpy as np, sherpa_onnx

MODEL_DIR = Path(os.getenv("MODEL_PATH", "/models"))
MODEL_NAME = os.getenv("MODEL_NAME", "default")
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=str(MODEL_DIR / os.getenv("ENCODER", "encoder.onnx")),
    decoder=str(MODEL_DIR / os.getenv("DECODER", "decoder.onnx")),
    joiner=str(MODEL_DIR / os.getenv("JOINER", "joiner.onnx")),
    tokens=str(MODEL_DIR / os.getenv("TOKENS", "tokens.txt")),
    num_threads=int(os.getenv("NUM_THREADS", "4")), provider="cpu",
    model_type=os.getenv("MODEL_TYPE", "transducer"),
    feature_dim=int(os.getenv("FEATURE_DIM", "80")),
)

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._json(200, {"object": "list", "data": [{"id": MODEL_NAME, "object": "model"}]})

    def do_POST(self):
        if self.path.rstrip("/") != "/v1/audio/transcriptions":
            return self._json(404, {"error": {"message": "not found"}})
        try:
            raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            b = re.search(r"boundary=([^;]+)", self.headers["Content-Type"], re.I).group(1).strip().strip('"').encode()
            part = next(p for p in raw.split(b"--" + b) if b'name="file"' in p)
            data = part.partition(b"\r\n\r\n")[2].removesuffix(b"\r\n")
            with wave.open(io.BytesIO(data), "rb") as w:
                samples = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
                sr = w.getframerate()
            s = rec.create_stream()
            s.accept_waveform(sr, samples)
            rec.decode_stream(s)
            self._json(200, {"text": s.result.text or ""})
        except Exception as e:
            self._json(400, {"error": {"message": str(e)}})

if __name__ == "__main__":
    host, port = os.getenv("HOST", "0.0.0.0"), int(os.getenv("PORT", "8080"))
    print(f"http://{host}:{port} model={MODEL_NAME}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
