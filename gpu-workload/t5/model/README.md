# T5 Model Docker container

Here we provide a Dockerfile that packages t5 model into a Docker container image. This is a self-complete multi stage build process:

Build stages:

1. Download the model from huggingface (notice git-lfs during git clone)
2. Create model package (MAR file)
3. Create a final docker container to serve model

## Build

You can configure the build process by setting docker build arguments:

* `BASE_IMAGE` - base image to use for the final container (default: `pytorch/torchserve:latest-cpu`)
* `MODEL_NAME` - name of the model to download from huggingface (default: `t5-small`)
* `MODEL_REPO` - repository of the model to download with git (default: `https://huggingface.co/${MODEL_NAME}`)
* `MODEL_VERSION` - version of the model to download from huggingface (default: `1`)

For CPU serving:

```bash
export MODEL_NAME='t5-small'
export MODEL_VERSION='1.0'
export MODEL_IMAGE="eu.gcr.io/$GOOGLE_CLOUD_PROJECT/models/$MODEL_NAME:$MODEL_VERSION-cpu"
docker build --tag "$MODEL_IMAGE" \
    --build-arg MODEL_NAME \
    --build-arg MODEL_VERSION'\
    .
```

For GPU serving:

```bash
export MODEL_NAME='t5-small'
export MODEL_VERSION='1.0'
export MODEL_IMAGE="eu.gcr.io/$GOOGLE_CLOUD_PROJECT/models/$MODEL_NAME:$MODEL_VERSION-gpu"

docker build --tag "$MODEL_IMAGE" \
    --build-arg BASE_IMAGE='pytorch/torchserve:latest-gpu' \
    --build-arg MODEL_NAME \
    --build-arg MODEL_VERSION'\
    .
```

## Run

```bash
docker run --rm -it -p '8080:8080' "$MODEL_IMAGE" torchserve --foreground --models "all"
```
