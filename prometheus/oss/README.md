# OSS Prometheus on GKE Autopilot

## Deploy OSS Prometheus

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install tutorial bitnami/kube-prometheus \
  --version 8.2.2 \
  --values values.yaml \
  --wait
```

## Deploy Bank of Anthos

```bash
git clone https://github.com/GoogleCloudPlatform/bank-of-anthos.git
kubectl apply -f bank-of-anthos/extras/jwt/jwt-secret.yaml
kubectl apply -f bank-of-anthos/kubernetes-manifests
```

## Prepare Slack notification

### Create the Slack application

1. Join a Slack workspace, either by registering with your email or by using an invitation sent by a Workspace Admin.

>Note: If you are not an Admin for your Slack workspace, you may need approval from a Workspace Admin before your app is deployed to your workspace.

2. Sign in to Slack using your workspace name and your Slack account credentials.

3. Create a new Slack app:
    * In the Create an app dialog, click From scratch.
    * Specify an App Name and choose your Slack workspace.
    * Click Create App.
    * Under Add features and functionality, click Incoming Webhooks.
    * Click the Activate Incoming Webhooks toggle.
    * In the Webhook URLs for Your Workspace section, click Add New Webhook to Workspace.
    * On the authorization page that opens, select a channel to receive notifications.
    * Click Allow.
    * A webhook for your Slack application is displayed in the Webhook URLs for Your Workspace section. Save the URL for later.

### Create a Kubernetes secret with Slack Webhook URL

Replace `<slack_app_webhook_url>` with your value

```bash
kubectl create secret generic alertmanager-slack-webhook --from-literal webhookURL=<slack_app_webhook_url>
```

## Create Prometheus custom resources

```bash
kubectl apply -f probes.yaml
kubectl apply -f rules.yaml
kubectl apply -f alertmanagerconfig.yaml
```

## Testing alerts notifications

Let's simulate outage of `userservice` service

```bash
kubectl scale deployment userservice --replicas 0
```

Wait while you get notification in your Slack channel.

Restore `userservice` deployment

```bash
kubectl scale deployment userservice --replicas 1
```

After prox. 5 min you will recieve notification that service is restored.

## Clean up

```bash
kubectl delete -f bank-of-anthos/kubernetes-manifests
helm uninstall tutorial
```
