# container-packaged-ai-models
AI Models stored in container images

## From [Hugging Face](https://huggingface.co/models)

1. [openai/gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b)
   - Dockerhub: `docker.io/moosestack/packaged-model-openai_gpt-oss-20b:latest`
   - Build Example: `podman build --build-arg HUGGINGFACE_MODEL_REPO=openai/gpt-oss-20b -t gpt-oss-20b:latest ./huggingface`

2. [ggml-org/gpt-oss-20b-GGUF](https://huggingface.co/ggml-org/gpt-oss-20b-GGUF)
   - Dockerhub: `docker.io/moosestack/gpt-oss-20b-mxfp4-gguf_packaged-modelcar:latest`
   - Build Example: `podman build --build-arg HUGGINGFACE_MODEL_REPO=ggml-org/gpt-oss-20b-GGUF -t gpt-oss-20b-gguf:latest ./huggingface`