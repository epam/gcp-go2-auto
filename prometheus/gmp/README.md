# GMP on GKE Autopilot

## Create GKE autopilot

>Note: only GKE with version 1.25 and later supports GMP

```bash
gcloud container clusters create-auto prometheus \
  --region=us-central1 \
  --release-channel=rapid \
  --cluster-version=1.25.4-gke.1600
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

### Create a Kubernetes secret with Alertmanager configuration

Replace value of `SLACK_WEBHOOK_URL` variable with Webhook URL saved in previous section.

```bash
SLACK_WEBHOOK_URL=""
sed -i "s@SLACK_WEBHOOK_URL@$SLACK_WEBHOOK_URL@g" "alertmanager.yaml"
```

Create Kubernetes secret

```bash
kubectl create secret generic alertmanager \
  -n gmp-public \
  --from-file=alertmanager.yaml
```

## Prometheus UI

Details could be found in [official docs](https://cloud.google.com/stackdriver/docs/managed-prometheus/query#ui-prometheus)

## Deploy Blackbox Exporter

```bash
kubectl apply -f blackbox-exporter.yaml
```

## Create GMP custom resources

```bash
kubectl apply -f probes.yaml
kubectl apply -f rules.yaml
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
