ARG BASE_IMAGE=pytorch/torchserve:latest-cpu

FROM alpine/git

ARG MODEL_NAME=t5-small
ARG MODEL_REPO=https://huggingface.co/${MODEL_NAME}
RUN git clone "${MODEL_REPO}" /model

FROM ${BASE_IMAGE}

ARG MODEL_NAME
ARG MODEL_VERSION=1.0

COPY --from=0 /model/. /home/model-server/
COPY handler.py \
     model.py \
     requirements.txt \
     setup_config.json /home/model-server/

RUN  torch-model-archiver \
     --model-name "${MODEL_NAME}" \
     --version "${MODEL_VERSION}" \
     --model-file 'model.py' \
     --serialized-file "pytorch_model.bin" \
     --handler 'handler.py' \
     --extra-files "config.json,spiece.model,tokenizer.json,setup_config.json" \
     --runtime 'python' \
     --export-path "model-store" \
     --requirements-file "requirements.txt"

FROM ${BASE_IMAGE}

# for pip install
ENV PATH /home/model-server/.local/bin:$PATH
ENV TS_CONFIG_FILE /home/model-server/config.properties
# CPU inference will trhow a warning cuda warning (not error)
# Could not load dynamic library 'libnvinfer_plugin.so.7'
# This is expected behaviour. see: https://stackoverflow.com/a/61137388
ENV TF_CPP_MIN_LOG_LEVEL 2

COPY --from=1 /home/model-server/model-store/ /home/model-server/model-store
COPY requirements.txt /home/model-server/
RUN pip install -r requirements.txt --no-cache-dir --user
