### Building
Build the shared runtime image first, then build this model image:

```bash
podman build \
	-t sherpa-onnx-runtime:latest \
	-f inference-runtimes/sherpa-onnx/Containerfile inference-runtimes/sherpa-onnx

podman build --squash \
	-t docker.io/moosestack/sherpa-onnx_parakeet-tdt-0.6b-v3-int8_cpu-x86-64:latest \
	inference-runtimes/sherpa-onnx/parakeet-tdt-0.6b-v3-int8
```

### Running
OpenAI-compatible HTTP API (`POST /v1/audio/transcriptions`) on port 8080:

```bash
podman run --rm -it \
	-p 8080:8080 \
	docker.io/moosestack/sherpa-onnx_parakeet-tdt-0.6b-v3-int8_cpu-x86-64:latest
```

### Test
Record from the mic until Ctrl+C, or pass a mono 16-bit PCM WAV:

```bash
python3 -m pip install pyaudio
python3 inference-runtimes/sherpa-onnx/parakeet-tdt-0.6b-v3-int8/speech-to-text-test.py
```

Optional: `SHERPA_ONNX_URL` (default `http://127.0.0.1:8080`), `SHERPA_ONNX_API_KEY`.

```bash
curl -s http://127.0.0.1:8080/v1/audio/transcriptions \
  -F file=@recording.wav \
  -F model=parakeet-tdt-0.6b-v3-int8
```
