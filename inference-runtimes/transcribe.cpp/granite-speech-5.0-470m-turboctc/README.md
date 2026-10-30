### Building
Package the GGUF modelcar (Q8_0 only), build the shared runtime, then build this model image:

```bash
podman build --squash \
	--build-arg HUGGINGFACE_ALLOW_PATTERNS="*Q6_K.gguf" \
	--build-arg HUGGINGFACE_MODEL_REPO=handy-computer/granite-speech-5.0-470m-turboctc-gguf \
	-t docker.io/moosestack/granite-speech-5.0-470m-turboctc-gguf_packaged-modelcar:latest \
	./huggingface

podman build --build-arg TRANSCRIBE_CPP_VERSION=0.4.1 \
	-t transcribe-cpp-runtime:latest \
	-f inference-runtimes/transcribe.cpp/Containerfile inference-runtimes/transcribe.cpp

podman build --squash \
	-t docker.io/moosestack/transcribe-cpp_granite-speech-5.0-470m-turboctc_cpu-x86-64:latest \
	inference-runtimes/transcribe.cpp/granite-speech-5.0-470m-turboctc
```

### Running
OpenAI-compatible HTTP API (`POST /v1/audio/transcriptions`) on port 8080.
Audio must be **16 kHz mono 16-bit PCM WAV** (offline / batch only — not streaming):

```bash
podman run --rm -it \
	-p 8080:8080 \
	docker.io/moosestack/transcribe-cpp_granite-speech-5.0-470m-turboctc_cpu-x86-64:latest
```

### Deploying with kubectl
```bash
kubectl apply -f https://raw.githubusercontent.com/MooseStack/container-packaged-ai-models/main/kubernetes/manifests/granite-speech-transcribecpp-asr.yaml
```

### Deploying with Helm
```bash
helm install granite-speech-transcribecpp-asr \
  git+https://github.com/MooseStack/container-packaged-ai-models@kubernetes/helm?ref=main \
  -f https://raw.githubusercontent.com/MooseStack/container-packaged-ai-models/main/kubernetes/helm/values/granite-speech-transcribecpp-asr.yaml
```

Add `--set ingress.enabled=true` or `--set route.enabled=true` for Ingress or an OpenShift Route.

### Test
Record from the mic until Ctrl+C, or pass a mono 16-bit PCM 16 kHz WAV:

```bash
python3 -m pip install -r inference-runtimes/transcribe.cpp/granite-speech-5.0-470m-turboctc/requirements.txt
python3 inference-runtimes/transcribe.cpp/granite-speech-5.0-470m-turboctc/speech-to-text-test.py
python3 inference-runtimes/transcribe.cpp/granite-speech-5.0-470m-turboctc/speech-to-text-test.py recording.wav
```

Optional: `TRANSCRIBE_CPP_URL` (default `http://127.0.0.1:8080`), `TRANSCRIBE_CPP_API_KEY`.

```bash
curl -s http://127.0.0.1:8080/v1/audio/transcriptions \
  -F file=@recording.wav \
  -F model=granite-speech-5.0-470m-turboctc
```
