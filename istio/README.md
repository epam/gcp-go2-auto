# Secure Kubernetes Services with Istio on GKE Autopilot

## Create GKE Autopilot

```shell
gcloud container clusters create-auto istio \
  --region=us-central1 \
  --workload-policies=allow-net-admin
```

## Install Istion with IstioCTL

```shell
istioctl install --set profile=default -y
```

## Deploy Bank of Anthos

### Configure istio sidecar container injection

```shell
kubectl label namespace default istio-injection=enabled
```

### Deploy app

Configure workload identity:????????

```shell
git clone https://github.com/GoogleCloudPlatform/bank-of-anthos.git
kubectl apply -f bank-of-anthos/extras/jwt/jwt-secret.yaml
kubectl apply -f bank-of-anthos/kubernetes-manifests
```

## Configure Istio for Bank of Anthos

### Create Istio Gateway

```shell
kubectl apply -f bank-of-anthos/extras/istio/frontend-ingress.yaml
```

### Create PeerAuthentication with mTLS

```shell
kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
      mode: STRICT
EOF
```

## Verify mTLS configuration with Kiali

<https://cloud.google.com/stackdriver/docs/managed-prometheus/query>

### Create Google Service Account for query interface workload

```shell
gcloud iam service-accounts create monitoring \
  --display-name="Service account for GMP query interface"
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member "serviceAccount:monitoring@PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/monitoring.viewer
gcloud iam service-accounts add-iam-policy-binding \
  gmp-query@PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:PROJECT_ID.svc.id.goog[monitoring/default]"
```

### Install GMP query interface

```shell
kubectl create namespace monitoring
kubectl -n monitoring apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/prometheus-engine/v0.7.1/examples/frontend.yaml
kubectl annotate serviceaccount --namespace monitoring \
  default \
  iam.gke.io/gcp-service-account=monitoring@PROJECT_ID.iam.gserviceaccount.com --overwrite
```

### Install Kiali

```shell
helm repo add kiali https://kiali.org/helm-charts
helm repo update
helm install \
  --namespace kiali-operator \
  --create-namespace \
  kiali-operator \
  kiali/kiali-operator
kubectl apply -f kiali.yaml
```

### View Kiali dashboard

```shell
kubectl -n istio-system port-forward svc/kiali 20001
```

## Clean up

```shell
kubectl delete -f kiali.yaml
helm uninstall --namespace kiali-operator kiali-operator
kubectl -n monitoring delete -f https://raw.githubusercontent.com/GoogleCloudPlatform/prometheus-engine/v0.7.1/examples/frontend.yaml
kubectl delete -f extras/istio/frontend-ingress.yaml
kubectl delete -f kubernetes-manifests
istioctl uninstall --purge -y
gcloud container clusters delete --region us-central1 istio --quiet
```
