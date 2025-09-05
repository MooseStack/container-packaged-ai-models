## Stage 1: Modelcar to download the model
FROM docker.io/moosestack/gpt-oss-20b-mxfp4-gguf_packaged-modelcar:latest as modelcar

## Stage 2: Llama.cpp
FROM ghcr.io/ggml-org/llama.cpp:server-b6265

WORKDIR /app

# Copy the model files from the modelcar into the vLLM container
COPY --from=modelcar /models /models

EXPOSE 8080

## using sh -c to allow shell expansion for *.gguf
## using \"$@\"", "--" to separate CMD args from ENTRYPOINT args
ENTRYPOINT ["/bin/sh", "-c", "/app/llama-server --model /models/*.gguf --jinja -c 0 \"$@\"", "--"]

# Each item here is passed literally, spaces included
CMD ["--port", "8080", "--host", "0.0.0.0"]
