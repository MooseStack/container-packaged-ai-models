# container-packaged-ai-models
AI Models stored in container images

## From [Hugging Face](https://huggingface.co/models)

1. [openai/gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b)
   - Dockerhub: `docker.io/moosestack/packaged-model-openai_gpt-oss-20b:latest`
   - Build Example: `podman build --build-arg HUGGINGFACE_MODEL_REPO=openai/gpt-oss-20b -t gpt-oss-20b:latest ./huggingface`