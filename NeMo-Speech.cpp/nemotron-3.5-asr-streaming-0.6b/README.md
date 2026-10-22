### Building
Build the shared runtime image first, then build this model image:

```bash
podman build --build-arg NEMO_SPEECH_VERSION=0.2.0 \
	-t nemo-speech-runtime:latest \
	-f NeMo-Speech.cpp/Containerfile NeMo-Speech.cpp

podman build --squash \
	-t nemotron-3.5-asr-streaming-0.6b:latest \
	NeMo-Speech.cpp/nemotron-3.5-asr-streaming-0.6b
```

### Running
Run the speech server and publish its HTTP/WebSocket port:

```bash
podman run --rm -it \
	-p 8080:8080 \
	nemotron-3.5-asr-streaming-0.6b:latest
```

### Deploying with kubectl
```bash
kubectl apply -k https://github.com/MooseStack/container-packaged-ai-models.git/kubernetes/kustomize/overlays/nemotron-asr?ref=main
```

Use `nemotron-asr-ingress` or `nemotron-asr-openshift` instead for Ingress or an OpenShift Route.

### Deploying with Helm
```bash
helm install nemotron-asr \
  git+https://github.com/MooseStack/container-packaged-ai-models@kubernetes/helm?ref=main \
  -f https://raw.githubusercontent.com/MooseStack/container-packaged-ai-models/main/kubernetes/helm/values/nemotron-asr.yaml
```

Add `--set ingress.enabled=true` or `--set route.enabled=true` for Ingress or an OpenShift Route.

### HTTPS streaming client
The speech test client supports secure WebSocket endpoints. Set `NEMO_SPEECH_WS_URL` to the `wss://` realtime endpoint and set `NEMO_SPEECH_API_KEY` when the server requires authentication:

`NEMO_SPEECH_WS_URL=wss://speech.example.com/v1/realtime NEMO_SPEECH_API_KEY=your-key python3 speech-to-text-test.py`

- Default is ws://127.0.0.1:8080/v1/realtime

With the container running, execute `speech-to-text-test.py` on the host and press `Ctrl+C` when you are finished speaking.

```bash
python3 NeMo-Speech.cpp/nemotron-3.5-asr-streaming-0.6b/speech-to-text-test.py
```