# T5 Model Serving

Stanza for model packaging and serving for T5 models.

## Package Model

```bash
export GOOGLE_CLOUD_PROJECT=$(gcloud config get project)
export MODEL_NAME="t5-small"
export MODEL_VERSION="1.0"
export MACHINE="cpu"
export MODEL_IMAGE="gcr.io/$GOOGLE_CLOUD_PROJECT/models/$MODEL_NAME:$MODEL_VERSION-$MACHINE"
docker buildx build \
  --build-arg BASE_IMAGE="pytorch/torchserve:latest-$MACHINE" \
  --build-arg MODEL_NAME \
  --build-arg MODEL_VERSION \
  --tag "$MODEL_IMAGE" model
```

## Storing Model in GCR

```bash
gcloud auth configure-docker eu.gcr.io --quiet
docker push "$MODEL_IMAGE"
```

## Serving

```bash
docker run --rm -it -p "8080:8080" -p "8081:8081" "$MODEL_IMAGE" torchserve --start --foreground
```

## Testing

```bash
curl -v -X POST -H 'Content-Type: application/json' -d '{"text": "this is a test sentence", "from": "en", "to": "es"}' "http://0.0.0.0:8080/predictions/$MODEL_NAME/$MODEL_VERSION"
```

## Running the Client App

```bash
cd client-app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./src/app.py
```

> Now, with your browser open: <http://localhost:8050>
