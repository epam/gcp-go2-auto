# The Client App

Simple Client Application base on [fastdash](https://fastdash.app/) Python module.

## Package App

```bash
export IMAGE="eu.gcr.io/$GOOGLE_CLOUD_PROJECT/apps/fastdash:latest"
docker buildx build --tag "$IMAGE" .
```

## Storing the Client App

```bash
gcloud auth configure-docker eu.gcr.io --quiet
docker push "$IMAGE"
```

## Run

### Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./src/app.py
```

### Docker image

```bash
docker run -it --rm -p "8050:8050" $IMAGE
```
