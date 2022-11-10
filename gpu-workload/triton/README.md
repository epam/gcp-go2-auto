# ML model serving with Triton Inference Server on GKE Autopilot

This tutorial show how to run GPU workload on GKE Autopilot. As example of GPU workload Triton Inference Server is used.

Tutorial works in GCP CloudShell environment.

## Prepare model regestry for Triton Inference Server

Download and organize model artifacts as per Triton model repository spec

MODEL_URL="https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4?tf-hub-format=compressed"

```bash
LOCATION="us-central1"
MODEL_URL="https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-12_H-128_A-2/2?tf-hub-format=compressed"
BUCKET_NAME="triton-models-repo"
MODEL_DIR="./models/bert"

mkdir -p "$MODEL_DIR/1/model.savedmodel/"
curl -L "$MODEL_URL" | tar -zxvC "$MODEL_DIR/1/model.savedmodel/"
gsutil mb -l "$LOCATION" "gs://$BUCKET_NAME"
gsutil -m cp -r "$MODEL_DIR" "gs://$BUCKET_NAME/"
```

## Create GKE Autopilot

Use version of GKE >= 1.24 to be able to run GPU workload

```bash
GKE_NAME="triton"

gcloud container clusters create-auto "$GKE_NAME" \
    --region="$LOCATION" \
    --release-channel="rapid" \
    --cluster-version="1.24.5-gke.600"

gcloud beta container clusters update "$GKE_NAME" \
    --region="$LOCATION" \
    --disable-managed-prometheus

kubectl create clusterrolebinding cluster-admin-binding --clusterrole cluster-admin --user "$(gcloud config get-value account)"
```

Execution of these commands take some time.

If needed obtain access to GKE

```bash
gcloud container clusters get-credentials "$GKE_NAME" --region="$LOCATION"
```

## Create Google Service Account to get access to Cloud Storage

```bash
GSA_NAME="triton-inference-server"
GSA_EMAIL="$GSA_NAME@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com"

gcloud iam service-accounts create "$GSA_NAME"

gcloud projects add-iam-policy-binding \
    "$GOOGLE_CLOUD_PROJECT" \
    --member "serviceAccount:$GSA_EMAIL" \
    --role "roles/storage.admin"

gcloud iam service-accounts add-iam-policy-binding \
    "$GSA_EMAIL" \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$GOOGLE_CLOUD_PROJECT.svc.id.goog[default/default]"

kubectl annotate serviceaccount "default" "iam.gke.io/gcp-service-account=$GSA_EMAIL"

# Triron inference server works only with GOOGLE_APPLICATION_CREDENTIALS file
gcloud iam service-accounts keys create key.json --iam-account "$GSA_EMAIL"
kubectl create secret generic "$GSA_NAME" --from-file=key.json=key.json

# HPA setup
gcloud projects add-iam-policy-binding \
    "$GOOGLE_CLOUD_PROJECT" \
    --member "serviceAccount:$GSA_EMAIL" \
    --role "roles/monitoring.viewer"

gcloud iam service-accounts add-iam-policy-binding \
    "$GSA_EMAIL" \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$GOOGLE_CLOUD_PROJECT.svc.id.goog[custom-metrics/custom-metrics-stackdriver-adapter]"

# Custom metrics for HPA setup
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/k8s-stackdriver/master/custom-metrics-stackdriver-adapter/deploy/production/adapter_new_resource_model.yaml

kubectl annotate serviceaccount --namespace "custom-metrics" \
    "custom-metrics-stackdriver-adapter" \
    "iam.gke.io/gcp-service-account=$GSA_EMAIL"
```

## Deployment of Triton Inference Server

```bash
kubectl apply -f triton.yaml
```

## HPA setup

```bash
kubectl apply -f hpa.yaml
```

## Load generator script

To get IP address of Triton server

```bash
kubectl get ingress triton-inference-server -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

Edit `loadgenerator.yaml` and replace `<triton-ip-address>` with IP address of triton server

```bash
kubectl apply -f loadgenerator.yaml
kubectl port-forward "svc/loadgenerator" 8080
```

With your internet browser visit: <http://localhost:8080>.
The load generator has auto-start enabled by default. You should be able to observe it's execution

## Clean up

```bash
# Delete GKE cluster
kubectl delete -f loadgenerator.yaml -f triton.yaml -f hpa.yaml
gcloud container clusters delete "triton" --region="$LOCATION"

# Cleanup GSA
gcloud projects remove-iam-policy-binding \
    $GOOGLE_CLOUD_PROJECT \
    --member="serviceAccount:$GSA_EMAIL" \
    --role="storage.admin"

gcloud projects remove-iam-policy-binding \
    $GOOGLE_CLOUD_PROJECT \
    --member="serviceAccount:$GSA_EMAIL" \
    --role="roles/monitoring.viewer"

gcloud iam service-accounts delete "$GSA_EMAIL" --quiet
```
