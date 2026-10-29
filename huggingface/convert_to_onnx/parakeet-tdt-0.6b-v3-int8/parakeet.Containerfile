## STAGE 1. Download Hugging Face NeMo checkpoint (same pattern as convert_to_onnx/Containerfile)
## Build from huggingface/:
##   podman build --squash \
##     --build-arg HUGGINGFACE_MODEL_REPO=nvidia/parakeet-tdt-0.6b-v3 \
##     --build-arg HUGGINGFACE_ALLOW_PATTERNS="*.nemo" \
##     -t docker.io/moosestack/parakeet-tdt-0.6b-v3-onnx-int8_packaged-modelcar:latest \
##     -f convert_to_onnx/parakeet-tdt-0.6b-v3-int8/parakeet.Containerfile \
##     ./huggingface
FROM registry.access.redhat.com/ubi9/python-311:latest AS download

USER root

ARG HUGGINGFACE_MODEL_REPO=nvidia/parakeet-tdt-0.6b-v3
ARG HUGGINGFACE_ALLOW_PATTERNS="*.nemo"
ENV HUGGINGFACE_MODEL_REPO=${HUGGINGFACE_MODEL_REPO}
ENV HUGGINGFACE_ALLOW_PATTERNS=${HUGGINGFACE_ALLOW_PATTERNS}

RUN pip install --no-cache-dir huggingface-hub

COPY download_model.py .

RUN python download_model.py


## STAGE 2. NeMo Parakeet → ONNX (encoder / decoder / joiner + int8)
FROM registry.access.redhat.com/ubi9/python-311:latest AS convert

USER root

WORKDIR /workspace/parakeet

# CPU torch first so nemo does not pull a CUDA wheel
RUN pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        torch

COPY convert_to_onnx/parakeet-tdt-0.6b-v3-int8/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY convert_to_onnx/parakeet-tdt-0.6b-v3-int8/generate_bpe_vocab.py /workspace/generate_bpe_vocab.py
COPY convert_to_onnx/parakeet-tdt-0.6b-v3-int8/nemo-to-onnx.py .
COPY --from=download /models /models

# Script expects ./parakeet-tdt-0.6b-v3.nemo in cwd
RUN ln -sf /models/parakeet-tdt-0.6b-v3.nemo ./parakeet-tdt-0.6b-v3.nemo && \
    python nemo-to-onnx.py && \
    test -f encoder.int8.onnx && \
    test -f decoder.int8.onnx && \
    test -f joiner.int8.onnx && \
    test -f tokens.txt && \
    mkdir -p /models-out && \
    cp -a *.int8.onnx *.txt /models-out/


## STAGE 3. Modelcar with int8 ONNX + tokens only
FROM registry.access.redhat.com/ubi10/ubi-micro:latest

LABEL org.opencontainers.image.source="https://github.com/MooseStack/container-packaged-ai-models"

COPY --from=convert /models-out/ /models/

RUN chmod -Rf 775 /models

USER 1001
