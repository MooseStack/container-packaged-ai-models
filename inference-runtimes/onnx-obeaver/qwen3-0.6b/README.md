### Building
Build the shared oBeaver runtime image first, then build this model image:

```bash
podman build \
	-t onnx-obeaver-runtime:latest \
	-f inference-runtimes/onnx-obeaver/Containerfile inference-runtimes/onnx-obeaver

podman build --squash \
	-t docker.io/moosestack/onnx-obeaver_qwen3-0.6b_cpu-x86-64:latest \
	inference-runtimes/onnx-obeaver/qwen3-0.6b
```

### Running
OpenAI-compatible HTTP API (Microsoft [oBeaver](https://github.com/microsoft/obeaver) + ONNX Runtime GenAI) on port 8080:

```bash
podman run --rm -it \
	-p 8080:8080 \
	docker.io/moosestack/onnx-obeaver_qwen3-0.6b_cpu-x86-64:latest
```

### Deploying with kubectl
```bash
kubectl apply -f https://raw.githubusercontent.com/MooseStack/container-packaged-ai-models/main/kubernetes/manifests/qwen3-0.6b-onnx-obeaver-text.yaml
```

### Deploying with Helm
```bash
helm install qwen3-0.6b-onnx-obeaver-text \
  git+https://github.com/MooseStack/container-packaged-ai-models@kubernetes/helm?ref=main \
  -f https://raw.githubusercontent.com/MooseStack/container-packaged-ai-models/main/kubernetes/helm/values/qwen3-0.6b-onnx-obeaver-text.yaml
```

Add `--set ingress.enabled=true` or `--set route.enabled=true` for Ingress or an OpenShift Route.

### Test
```bash
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3-0.6b","messages":[{"role":"user","content":"Tell me a joke."}],"max_tokens":64}'
```

Or with the Python smoke client (stdlib only):

```bash
python3 inference-runtimes/onnx-obeaver/qwen3-0.6b/chat-completions-test.py
python3 inference-runtimes/onnx-obeaver/qwen3-0.6b/chat-completions-test.py "What is 2+2?"
```

Env overrides: `ONNX_GENAI_URL` (default `http://127.0.0.1:8080`), `ONNX_GENAI_MODEL`.

Base URL for OpenAI SDKs: `http://127.0.0.1:8080/v1`
