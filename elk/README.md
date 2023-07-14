# ELK

## GKE clsuter

### Create cluster

```bash
gcloud container clusters create-auto elk-stack \
  --region="us-central1"
```

### Enable Control Plane metrics

[Control Plane metrics guide](https://cloud.google.com/stackdriver/docs/solutions/gke/managing-metrics#enable-control-plane-metrics)

```bash
gcloud container clusters update elk-stack \
  --region=us-central1 \
  --monitoring=SYSTEM,API_SERVER,SCHEDULER,CONTROLLER_MANAGER
```

## Install ECK Operator

```bash
helm repo add elastic https://helm.elastic.co
helm repo update

helm upgrade --install "elastic-operator" "elastic/eck-operator" \
  --version="2.8.0" \
  --create-namespace \
  --namespace="elastic-system" \
  --set="resources.limits.cpu=250m" \
  --set="resources.limits.memory=512Mi" \
  --set="resources.limits.ephemeral-storage=1Gi" \
  --set="resources.requests.cpu=250m" \
  --set="resources.requests.memory=512Mi" \
  --set="resources.requests.ephemeral-storage=1Gi"
```

## ELK Stack

### Install

```bash
helm install kube-state-metrics prometheus-community/kube-state-metrics --namespace elastic-system
kubectl --namespace elastic-system apply -f elasticsearch.yaml
kubectl --namespace elastic-system apply -f kibana.yaml
kubectl --namespace elastic-system apply -f fleet-server.yaml
```

### Watch status

```bash
kubectl --namespace elastic-system get elasticsearches.elasticsearch.k8s.elastic.co,kibanas.kibana.k8s.elastic.co,agents.agent.k8s.elastic.co
```

## Clean up

```bash
kubectl --namespace elastic-system delete -f fleet-server.yaml
kubectl --namespace elastic-system delete -f kibana.yaml
kubectl --namespace elastic-system delete -f elasticsearch.yaml
helm uninstall kube-state-metrics --namespace elastic-system
helm uninstall elastic-operator --namespace elastic-system
gcloud dns record-sets delete "elk.epam.devops.delivery" \
  --type="A" \
  --zone="elk" \
  --quiet
gcloud compute addresses delete "elastic-stack" \
  --global \
  --quiet
gcloud container clusters delete "elk-stack" --location="us-central1" --quiet
```
