# T5 Model Serving

Stanza for model packaging and serving for T5 models.

## Package Model

```bash
export MODEL_NAME='t5-base'
export MODEL_DIR="models/$MODEL_NAME"
export MODEL_VERSION="1.0"

mkdir -p "model-store"
torch-model-archiver --force \
  --model-name "$MODEL_NAME" \
  --version "$MODEL_VERSION" \
  --model-file './model/model.py' \
  --serialized-file "$MODEL_DIR/pytorch_model.bin" \
  --handler './model/handler.py' \
  --extra-files "$MODEL_DIR/config.json,$MODEL_DIR/spiece.model,$MODEL_DIR/tokenizer.json,./model/setup_config.json" \
  --runtime 'python' \
  --export-path "model-store" -r ./model/requirements.txt
```

## Storing model in GCR

```bash
export MACHINE="cpu"
gcloud components install docker-credential-gcr
docker-credential-gcr configure-docker
docker-credential-gcr gcr-login
docker build \
  --build-arg BASE_IMAGE="pytorch/torchserve:latest-$MACHINE" \
  --build-arg MODEL_NAME \
  --build-arg MODEL_VERSION \
  --tag "gcr.io/$GOOGLE_CLOUD_PROJECT/models/$MODEL_NAME:$MODEL_VERSION-$MACHINE" model
docker push "gcr.io/$GOOGLE_CLOUD_PROJECT/models/$MODEL_NAME:$MODEL_VERSION-$MACHINE"
```

Verify model

```bash
docker run --rm -it -p '8080:8080'  "eu.gcr.io/$GOOGLE_CLOUD_PROJECT/models/$MODEL_NAME:$MODEL_VERSION-$MACHINE"
```

## Serving 

```bash
export TS_CONFIG_FILE="config.properties"

torchserve --foreground
# or to start in background
torchserve --start 
```

> Now, with your browser open: http://localhost:8105

## Testing

```bash
curl -v -X POST -H 'Content-Type: application/json' -d '{"text": "this is a test sentence", "from": "en", "to": "es"}' "http://0.0.0.0:8080/predictions/$MODEL_NAME/$MODEL_VERSION"
```

## Running the app

```bash
pip install -r 'requirements.txt'
./src/main.py
```
