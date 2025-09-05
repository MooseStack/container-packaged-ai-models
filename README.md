# container-packaged-ai-models
AI Models stored in container images

## From [Hugging Face](https://huggingface.co/models)

1. [openai/gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b)
   - Dockerhub: `docker.io/moosestack/packaged-model-openai_gpt-oss-20b:latest`
   - Build Example: `podman build --build-arg HUGGINGFACE_MODEL_REPO=openai/gpt-oss-20b -t gpt-oss-20b:latest ./huggingface`

2. [ggml-org/gpt-oss-20b-GGUF](https://huggingface.co/ggml-org/gpt-oss-20b-GGUF)
   - Dockerhub: `docker.io/moosestack/gpt-oss-20b-mxfp4-gguf_packaged-modelcar:latest`
   - Build Example: `podman build --build-arg HUGGINGFACE_MODEL_REPO=ggml-org/gpt-oss-20b-GGUF -t gpt-oss-20b-gguf:latest ./huggingface`
   - Serve model using [llama.cpp](https://github.com/ggml-org/llama.cpp) on CPU:
     - podman build -t gpt-oss-20b-gguf/lamacpp-cpu:latest -f serving-models-examples/gpt-oss-20b-gguf/lamacpp-cpu.Containerfile
     - podman run -it -p 8080:8080 localhost/gpt-oss-20b-gguf/lamacpp-cpu:latest

3. [ibm-granite/granite-embedding-english-r2](https://huggingface.co/ibm-granite/granite-embedding-english-r2)
   - Dockerhub: `docker.io/moosestack/granite-embedding-english-r2_packaged-modelcar:latest`
   - Build Example: `podman build --build-arg HUGGINGFACE_MODEL_REPO=ibm-granite/granite-embedding-english-r2 -t ibm-granite/granite-embedding-english-r2:latest ./huggingface`