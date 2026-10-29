### Building
Build the shared runtime image first, then build this model image:

```bash
podman build --build-arg NEMO_SPEECH_VERSION=0.2.0 \
	-t nemo-speech-runtime:latest \
	-f inference-runtimes/NeMo-Speech.cpp/Containerfile inference-runtimes/NeMo-Speech.cpp

podman build --squash \
	-t parakeet-tdt-0.6b-v3:latest \
	inference-runtimes/NeMo-Speech.cpp/parakeet-tdt-0.6b-v3
```

### Running
Run the speech server and publish its HTTP port:

```bash
podman run --rm -it \
	-p 8080:8080 \
	parakeet-tdt-0.6b-v3:latest
```

### Deploying with kubectl
```bash
kubectl apply -f https://raw.githubusercontent.com/MooseStack/container-packaged-ai-models/main/kubernetes/manifests/parakeet-nemospeechcpp-asr.yaml
```

### Deploying with Helm
```bash
helm install parakeet-nemospeechcpp-asr \
  git+https://github.com/MooseStack/container-packaged-ai-models@kubernetes/helm?ref=main \
  -f https://raw.githubusercontent.com/MooseStack/container-packaged-ai-models/main/kubernetes/helm/values/parakeet-nemospeechcpp-asr.yaml
```

Add `--set ingress.enabled=true` or `--set route.enabled=true` for Ingress or an OpenShift Route.

### Offline transcription client
Parakeet TDT is offline-only (full-utterance recognition). The test client records from the microphone until `Ctrl+C`, then `POST`s a WAV to `/v1/audio/transcriptions`. You can also pass an existing WAV file.

```bash
python3 -m pip install -r inference-runtimes/NeMo-Speech.cpp/parakeet-tdt-0.6b-v3/requirements.txt

# Record from mic, then transcribe
python3 inference-runtimes/NeMo-Speech.cpp/parakeet-tdt-0.6b-v3/speech-to-text-test.py

# Or transcribe a WAV file
python3 inference-runtimes/NeMo-Speech.cpp/parakeet-tdt-0.6b-v3/speech-to-text-test.py recording.wav
```

Optional environment variables:

- `NEMO_SPEECH_URL` (default `http://127.0.0.1:8080`)
- `NEMO_SPEECH_API_KEY` when the server requires authentication
