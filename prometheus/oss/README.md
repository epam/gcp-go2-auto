# OSS Prometheus on GKE Autopilot

## Deploy OSS Prometheus

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install tutorial bitnami/kube-prometheus \
  --version 8.2.2 \
  --set="operator.kubeletService.enabled=false" \
  --set="exporters.node-exporter.enabled=false" \
  --set="exporters.kube-state-metrics.enabled=false" \
  --set="kubelet.enabled=false" \
  --set="kubeApiServer.enabled=false" \
  --set="kubeControllerManager.enabled=false" \
  --set="kubeScheduler.enabled=false" \
  --set="coreDns.enabled=false" \
  --set="kubeProxy.enabled=false" \
  --wait
```

## Deploy Bank of Anthos

```bash
git clone https://github.com/GoogleCloudPlatform/bank-of-anthos.git
kubectl apply -f bank-of-anthos/extras/jwt/jwt-secret.yaml
kubectl apply -f bank-of-anthos/kubernetes-manifests
```

## Create Probe custom resources

```bash
kubectl apply -f probes.yaml
```


