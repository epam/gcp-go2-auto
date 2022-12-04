# T5 Model Serving

Stanza for model packaging and serving for T5 models.

## Package Model

```bash
export MODEL_NAME='t5-small'
export MODEL_DIR="models/$MODEL_NAME"
export MODEL_VERSION="1.0"

mkdir -p "model_store"
torch-model-archiver \
  --model-name "$MODEL_NAME" \
  --version "$MODEL_VERSION" \
  --model-file './src/model.py' \
  --serialized-file "$MODEL_DIR/pytorch_model.bin" \
  --handler './src/handler.py' \
  --extra-files "$MODEL_DIR/config.json,$MODEL_DIR/spiece.model,$MODEL_DIR/tokenizer.json,setup_config.json" \
  --runtime 'python3' \
  --export-path "model_store" \
  -r 'requirements.txt' -f
```

## Storing model in GCR

```bash
gcloud components install docker-credential-gcr
docker-credential-gcr configure-docker
docker-credential-gcr gcr-login
docker build \
  --build-arg MODEL_NAME \
  --build-arg MODEL_VERSION \
  -t "eu.gcr.io/$GOOGLE_CLOUD_PROJECT/models/$MODEL_NAME:$MODEL_VERSION" \
  -f 'Dockerfile.torch' .
```

## Serving

```bash
export TS_CONFIG_FILE="config.properties"

torchserve --foreground
# or to start in background
torchserve --start
torchserve-dashboard --server.port '8105'
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
