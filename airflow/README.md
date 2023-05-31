# Airflow on GKE Autopilot

## GKE clsuter

Create cluster and enable GcsFuseCsiDriver

```bash
gcloud container clusters create-auto airflow \
  --release-channel="rapid" \
  --region="REGION"
```

## Create Cloud SQL and Service Account

```bash
gcloud compute addresses create google-managed-services-default \
  --global \
  --purpose=VPC_PEERING \
  --prefix-length=16 \
  --description="peering range for Google" \
  --network=default
gcloud services vpc-peerings connect \
  --service=servicenetworking.googleapis.com \
  --ranges=google-managed-services-default \
  --network=default
gcloud sql instances create airflow-metadata \
  --database-version=POSTGRES_11 \
  --cpu=1 \
  --memory=4GB \
  --region=REGION \
  --root-password=DB_ROOT_PASSWORD \
  --no-assign-ip \
  --network=default
gcloud sql databases create airflow-metadata \
  --instance=airflow-metadata
gcloud sql users create airflow-metadata \
  --instance=airflow-metadata \
  --password=DB_PASSWORD
```

```bash
gcloud iam service-accounts create airflow-metadata-db \
  --display-name="Airflow Metadata DB Service Account"
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member "serviceAccount:airflow-metadata-db@PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/cloudsql.client
gcloud iam service-accounts add-iam-policy-binding \
  airflow-metadata-db@PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:PROJECT_ID.svc.id.goog[airflow/airflow-metadata-db]"
```

```bash
kubectl create namespace airflow
kubectl apply -f cloud-sql-proxy.yaml
```

## Configure GCS

```bash
gcloud storage buckets create gs://PROJECT_ID-airflow-dags \
  --location="REGION"
gcloud iam service-accounts create airflow-dags-reader \
  --display-name="Airflow DAG reader from GCS bucket"
gcloud storage buckets add-iam-policy-binding gs://PROJECT_ID-airflow-dags \
  --member "serviceAccount:airflow-dags-reader@PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/storage.insightsCollectorService
gcloud storage buckets add-iam-policy-binding gs://PROJECT_ID-airflow-dags \
  --member "serviceAccount:airflow-dags-reader@PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/storage.objectViewer
gcloud iam service-accounts add-iam-policy-binding \
  airflow-dags-reader@PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:PROJECT_ID.svc.id.goog[airflow/airflow]"
gcloud beta container clusters update airflow \
  --update-addons="GcsFuseCsiDriver=ENABLED" \
  --region="REGION"
```

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: airflow
  namespace: airflow
  annotations:
    iam.gke.io/gcp-service-account: airflow-dags-reader@PROJECT_ID.iam.gserviceaccount.com
EOF
kubectl apply -f pvc.yaml
```

## Create DNS and IP and Load Balancer (Ingress)

```bash
gcloud compute addresses create "airflow" --global
gcloud dns managed-zones create "airflow" \
  --description="DNS Zone for Airflow" \
  --dns-name="airflow.BASE_DOMAIN" \
  --visibility="public"
gcloud dns record-sets create "airflow.BASE_DOMAIN" \
  --rrdatas="$(gcloud compute addresses describe "airflow" --global --format="value(address)")" \
  --ttl="300" \
  --type="A" \
  --zone="airflow"
```

```bash
kubectl apply -f ingress.yaml
```

## Authentication

Create secret with Google credentials

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: airflow-google-oauth-creds
  namespace: airflow
type: Opaque
data:
  GOOGLE_OAUTH_CLIENT_ID: $(echo -n "CLIENT_ID" | base64 -w0)
  GOOGLE_OAUTH_CLIENT_SECRET: $(echo -n "CLIENT_SECRET" | base64 -w0)
EOF
```

## Install Airflow

```bash
helm repo add apache-airflow https://airflow.apache.org
helm upgrade --install "airflow" "apache-airflow/airflow" \
  --version="1.9.0" \
  --namespace="airflow" \
  --values="values.yaml" \
  --set="fernetKey=FERNET_KEY" \
  --set="webserverSecretKey=WEBSERVER_SECRET_KEY" \
  --set="data.metadataConnection.pass=DB_PASSWORD"
```

## Clean Up

```bash
helm uninstall airflow --namespace airflow
kubectl delete -f cloud-sql-proxy.yaml
kubectl delete -f pvc.yaml
gcloud dns record-sets delete "airflow.BASE_DOMAIN" \
  --type="A" \
  --zone="airflow" \
  --quiet
gcloud compute addresses delete "airflow" \
  --global \
  --quiet
gcloud dns managed-zones delete "airflow" --quiet
gcloud sql instances delete airflow-metadata --quiet
gcloud container clusters delete airflow \
  --region="REGION" \
  --quiet
gcloud storage rm -r gs://PROJECT_ID-airflow-dags --quiet
gcloud storage buckets delete gs://PROJECT_ID-airflow-dags --quiet
gcloud iam service-accounts delete airflow-dags-reader@PROJECT_ID.iam.gserviceaccount.com --quiet
gcloud iam service-accounts delete airflow-metadata-db@PROJECT_ID.iam.gserviceaccount.com --quiet
gcloud services vpc-peerings delete \
  --service=servicenetworking.googleapis.com \
  --network=default \
  --quiet
gcloud compute addresses delete google-managed-services-default \
  --global \
  --quiet
```
