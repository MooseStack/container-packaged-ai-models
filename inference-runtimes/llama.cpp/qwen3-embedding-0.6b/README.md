### Building

Build the shared CPU runtime, then package it with the Qwen3 embedding modelcar:

```bash
podman build \
  -t llama-cpp-runtime:latest \
  -f inference-runtimes/llama.cpp/Containerfile inference-runtimes/llama.cpp

podman build --squash \
  -t docker.io/moosestack/llama-cpp_qwen3-embedding-0.6b_cpu-x86-64:latest \
  inference-runtimes/llama.cpp/qwen3-embedding-0.6b
```

### Running

Serve OpenAI-compatible embeddings on port 8080:

```bash
podman run --rm -it \
  -p 8080:8080 \
  docker.io/moosestack/llama-cpp_qwen3-embedding-0.6b_cpu-x86-64:latest
```

### Deploying with kubectl

```bash
kubectl apply -f https://raw.githubusercontent.com/MooseStack/container-packaged-ai-models/main/kubernetes/manifests/qwen3-0.6b-llamacpp-embedding.yaml
```

### Deploying with Helm

```bash
helm install qwen3-0.6b-llamacpp-embedding \
  git+https://github.com/MooseStack/container-packaged-ai-models@kubernetes/helm?ref=main \
  -f https://raw.githubusercontent.com/MooseStack/container-packaged-ai-models/main/kubernetes/helm/values/qwen3-0.6b-llamacpp-embedding.yaml
```

Add `--set ingress.enabled=true` or `--set route.enabled=true` for Ingress or an OpenShift Route.

### Test

Use the standard-library Python smoke client to check the response count and vector dimensions:

```bash
python3 test/embeddings.py "Embed this text!"
python3 test/embeddings.py --show-all "Embed this text!"
```

Override the endpoint with `--url` (or `EMBEDDINGS_URL`) and the model with `--model` (or `EMBEDDINGS_MODEL`). Use `--api-key` or `EMBEDDINGS_API_KEY` if authentication is enabled.

You can also call the endpoint directly:

```bash
curl -s http://127.0.0.1:8080/v1/embeddings \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3-embedding-0.6b","input":["Embed this text!"]}'
```

Base URL for OpenAI SDKs: `http://127.0.0.1:8080/v1`. The model name is `qwen3-embedding-0.6b`.
The image defaults to an 8,192-token context and one processing slot to keep CPU memory use bounded. Pass llama-server flags after the image name to change these settings.
