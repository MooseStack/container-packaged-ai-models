# container-packaged-ai-models
AI Models stored in container images

## From [Hugging Face](https://huggingface.co/models)

1. [openai/gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b)
   - Dockerhub: `docker.io/moosestack/packaged-model-openai_gpt-oss-20b:latest`
   - Build Example: `podman build --build-arg HUGGINGFACE_MODEL_REPO=openai/gpt-oss-20b -t gpt-oss-20b:latest ./huggingface`

2. [ggml-org/gpt-oss-20b-GGUF](https://huggingface.co/ggml-org/gpt-oss-20b-GGUF)
   - Dockerhub: `docker.io/moosestack/gpt-oss-20b-mxfp4-gguf_packaged-modelcar:latest`
   - Build Example: `podman build --build-arg HUGGINGFACE_MODEL_REPO=ggml-org/gpt-oss-20b-GGUF -t gpt-oss-20b-gguf:latest ./huggingface`
   - Serve model using [llama.cpp](https://github.com/ggml-org/llama.cpp) on an x86-64 CPU:
     - `podman run -it -p 8080:8080 docker.io/moosestack/llama-cpp_gpt-oss-20b-gguf_cpu-x86-64:latest`

3. [ibm-granite/granite-embedding-english-r2](https://huggingface.co/ibm-granite/granite-embedding-english-r2)
   - Dockerhub: `docker.io/moosestack/granite-embedding-english-r2_packaged-modelcar:latest`
   - Build Example: `podman build --build-arg HUGGINGFACE_MODEL_REPO=ibm-granite/granite-embedding-english-r2 -t ibm-granite/granite-embedding-english-r2:latest ./huggingface`

4. [Qwen/Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)-GGUF(converted)
   - Dockerhub: `docker.io/moosestack/qwen_qwen3-embedding-0.6b-gguf_packaged-modelcar:latest`
   - Build Example: `podman build --build-arg HUGGINGFACE_MODEL_REPO=Qwen/Qwen3-Embedding-0.6B -t qwen/qwen3-embedding-0.6b-gguf:latest ./convert_to_gguf`
