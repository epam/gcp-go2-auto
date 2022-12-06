ARG BASE_IMAGE=pytorch/torchserve:latest-cpu

FROM alpine/git

ARG MODEL_NAME=t5-small
ARG MODEL_REPO=https://huggingface.co/${MODEL_NAME}
RUN git clone "${MODEL_REPO}" /model

FROM ${BASE_IMAGE}

ARG MODEL_NAME=t5-small
ARG MODEL_VERSION=1.0

COPY --from=0 /model/. /home/model-server/
COPY handler.py \
     model.py \
     requirements.txt \
     setup_config.json /home/model-server/

RUN  mkdir -p model-store && \
     torch-model-archiver \
     --model-name "${MODEL_NAME}" \
     --version "${MODEL_VERSION}" \
     --model-file 'model.py' \
     --serialized-file "pytorch_model.bin" \
     --handler 'handler.py' \
     --extra-files "config.json,spiece.model,tokenizer.json,setup_config.json" \
     --runtime 'python3' \
     --export-path "model-store" \
     -r "requirements.txt"

FROM ${BASE_IMAGE}
# for pip install
ENV PATH /home/model-server/.local/bin:$PATH

COPY --from=1 /home/model-server/model-store/ /home/model-server/model-store

VOLUME [ "/home/model-server/model-store/" ]
