# Serving Predictions on GPU

This tutorials shows you how to setup a model serving on your Kubernetes cluster. We will deploy a PyTorch machine learning (ML) model that serves online predictions and serve the ML model with [TorchServe](https://pytorch.org/serve/) framework. TorchServe is a flexible and easy to use tool for serving PyTorch models. It provides out of the box support for all major deep learning frameworks, including PyTorch, TensorFlow, and ONNX. TorchServe can be used to deploy models in production, or for rapid prototyping and experimentation.

This tutorial will show you how to deploy pre-trained model into your GKE cluster:

* Download pre-trained T5 model from Hagging Face repository
* Prepare model for serving by packaging it as a Docker container image and pushing it to Google Container Registry (GCR)
* Deploy the model to your Kubernetes cluster
* Deploy a web application that communicates with the model

## About the model

T5 is a text-to-text transformer that converts text from one language to another where input and outputs are always the text strings, in contrast to BERT-style models that can only output either a class label or a span of the input. This model has been based on associated [paper](https://jmlr.org/papers/volume21/20-074/20-074.pdf) and [code](https://github.com/google-research/text-to-text-transfer-transformer] from Google Research.

The model is trained on a large number of text from [Colossal Clean Crawled Corpus (C4)](https://huggingface.co/datasets/c4) and [Wiki-DPR](https://huggingface.co/datasets/wiki_dpr)

There are several pre-trained versions available in the hugging face repository. All models below distributed under the Apache 2.0 license.

* [`t5-small`](https://huggingface.co/t5-small): 60M parameters (default)
* [`t5-base`](https://huggingface.co/t5-base): 220M parameters
* [`t5-large`](https://huggingface.co/t5-large): 770M parameters (3GB download)
* [`t5-3b`](https://huggingface.co/t5-3b): 2.7B parameters (11GB download)

Latest update [v1.1](https://github.com/google-research/text-to-text-transfer-transformer/blob/main/released_checkpoints.md#t511) of the model was released on 2021-03-25

* [`t5-v1_1-small`](https://huggingface.co/google/t5-v1_1-small): 220M parameters, update on t5 model (3GB download)
* [`t5-v1_1-base`](https://huggingface.co/google/t5-v1_1-base): 220M parameters, update on t5 model (3GB download)
* [`t5-v1_1-large`](https://huggingface.co/google/t5-v1_1-large): 220M parameters, update on t5 model (3GB download)

Other T5 model checkpoints you can find [here](https://huggingface.co/models?filter=t5)

## Before you begin

### Pricing

* GKE Autopilot is billed by the hour for the control plane and per second for the nodes in the cluster. [Learn more](https://cloud.google.com/kubernetes-engine/pricing#autopilot_pricing)

> You only pay for the CPU, memory, and storage that your workloads request while running on GKE Autopilot.

* Google Cloud Storage is billed per GB stored. [Learn more](https://cloud.google.com/storage/pricing). This storage will be used to store the model and application container images.

* GPU node pool is billed per second for the nodes in the cluster. [Learn more](https://cloud.google.com/kubernetes-engine/pricing#gpu_pricing)

### Deploy GKE Autopilot cluster

1. In the Google Cloud console, on the project selector page, select or [create a Google Cloud project](https://cloud.google.com/resource-manager/docs/creating-managing-projects)

2. Enable API access for the project
  
* [Enable the Kubernetes Engine API](https://console.cloud.google.com/flows/enableapi?apiid=container.googleapis.com)
* [Enable the Container Registry API](https://console.cloud.google.com/flows/enableapi?apiid=containerregistry.googleapis.com)
* [Enable the Cloud Storage API](https://console.cloud.google.com/flows/enableapi?apiid=storage-api.googleapis.com)

3. Create GKE Autopilot Cluster: [Learn more](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-an-autopilot-cluster)

4. Verify cluster mode

You can verify that your cluster is an Autopilot cluster by using the gcloud CLI.

```bash
export GOOGLE_CLOUD_PROJECT=[PROJECT_ID]
cloud container clusters describe [CLUSTER_NAME] --region [REGION]
```

The output contains the following:

```yaml
autopilot:
  enabled: true
```

5. Connect to your cluster

```bash
gcloud container clusters get-credentials [CLUSTER_NAME] \
    --region [REGION] \
    --project="$GOOGLE_CLOUD_PROJECT"
```

> This command configures `kubectl` to use the cluster you created. More about the tools see section below

### Tools used

* `gcloud` - Command-line tool for running Google Cloud Platform (GCP) commands. [Install gcloud](https://cloud.google.com/sdk/docs/install)
* `kubectl` - Command-line tool for running commands against Kubernetes clusters. [Install kubectl](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl)
* `docker` - Command-line tool for building and managing Docker containers. [Install docker](https://docs.docker.com/get-docker/)
* `git` - Command-line tool for managing source code. [Install git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* `Python 3.8 or higher` - Python is a programming language that lets you work quickly and integrate systems more effectively. [Install Python](https://www.python.org/downloads/)

## Deploy model for Serving

### Download pre-trained T5 model 

1. Clone this repository

```bash
git clone "https://github.com/epam/gcp-go2-auto.git"
cd 'gcp-go2-auto/gpu-workload/t5'
```

2. Download pre-trained model from Hagging Face repository 

The pre-trained model has been available in the [Hagging Face repository](https://huggingface.co/t5-small). You can download the model by running the following command:

```bash
export MODEL_NAME='t5-small'
git clone "huggingface.co/$MODEL_NAME" "models/$MODEL_NAME"
```

In this tutorial we will use `t5-small` model. This model is the fastest to download. However you may want to use a larger model for better performance.

> For larger model download may want to enable *git-lfs* to enable git cliet to download larger files. [Learn more](https://git-lfs.github.com/)

## Prepare model for Serving

There are several ways how you can package your model for serving. Depends on the model size and types of storage you can use different approaches. In this tutorial we will use the following approach:

* Package model as a Docker container image together with PyTorch Serving
* Push the image to Google Container Registry (GCR)
* Deploy the model to your Kubernetes cluster

Model packaging is a process of creating a Docker image that contains all the necessary files to run the model. The Docker image is then pushed to a container registry, such as Google Container Registry (GCR). The container registry is a repository for storing Docker images. The model server can then pull the image from the registry and run it. 

We will use Docker to create a container image that will be used to deploy the model to Kubernetes. The Dockerfile is already created for you. You can find it in the root directory of the repository.

This probably most simple approach to deploy your model into Kubernetes cluster. It will guarantee the model availability for the inference server, as both model and inference server are deployed as a single container. 

Other approaches you can find [here](https://pytorch.org/serve/inference_api.html#packaging-model-for-serving)


3. Build and push Docker image to GCR

File Dockerfile.torch serves as a template for building the Docker image. It contains multi-stage image build. 

The first stage is used to download the model artifacts from the Hugging Face repository. The second stage is used to package model with PyTorch Serving Archive tool ([torch-model-archiver](https://github.com/pytorch/serve/tree/master/model-archiver)). It will create a model archive (MAR) file that will be used by the inference server to load the model. The third stage is used to build the final image with PyTorch Serve that will be used to deploy the model to Kubernetes.

```bash
cd model/
export MODEL_VERSION='1.0'
export MACHINE='gpu'
export MODEL_IMAGE="gcr.io/$GOOGLE_CLOUD_PROJECT/models/$MODEL_NAME:$MODEL_VERSION-$MACHINE"
export BASE_IMAGE="pytorch/torchserve:latest-$MACHINE"
docker build \
  --build-arg BASE_IMAGE \
  --build-arg MODEL_NAME \
  --build-arg MODEL_VERSION \
  --tag "$MODEL_IMAGE" model/
docker push  "$MODEL_IMAGE" 
```

> Depending on selected model this operation can take some significant time

As you probably can see there are different base image for CPU and GPU. If you want to use CPU you then change `MACHINE` variable to `cpu`.

As the packaged model can be quite large it is recommended to use a container registry endpoint from the same location where you have deployed your GKE Autopilot Cluster. In this tutorial we will use `gcr.io` for US region. You can find the list of available regions [here](https://cloud.google.com/container-registry/docs/pushing-and-pulling#tag)

## Deploy model to Kubernetes

Kubernetes deployment manifests can be found in the `./kubernetes` directory.

Modify the `./kubernetes/serving-*.yaml` files to use the image you just pushed to GCR.

```bash
kubectl apply -f kubernetes/serving-gpu.yaml
# or for CPU serving 
kubectl apply -f kubernetes/serving-cpu.yaml
```

To validate successful deployment run the following command:

```bash
kubectl port-forward "svc/t5-inference" 8080
# you may need different terminal window
curl -v -X POST -H 'Content-Type: application/json' -d '{"text": "this is a test sentence", "from": "en", "to": "es"}' "http://localhost:8080/predictions/$MODEL_NAME/$MODEL_VERSION"
```

### Access deployed model with the application

1. Build and push application as a Docker image to GCR

```bash
export APP_IMAGE="gcr.io/$GOOGLE_CLOUD_PROJECT/apps/fastdash:latest"
docker build -t "$APP_IMAGE" .
docker push "$APP_IMAGE"
```

2. Deploy application to Kubernetes

Before you deploy application to Kubernetes you need to modify the `./kubernetes/app.yaml` file. Replace code below with the image you just pushed to GCR.

```yaml
image: APP_IMAGE
``

```bash
kubectl apply -f "kubernetes/app.yaml"
```

Wait until the application is deployed. Your kubectl command should return ready replicas 

```bash
kubectl get -f 'kubernetes/application.yaml'

# Result of the command
# NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
# deployment.apps/fastdash   1/1     1            0           1m
#
#NAME               TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
#service/fastdash   NodePort   10.43.241.112   <none>        8050/TCP         1m
```

You will see ready replicas when your application has been deployed. 

3. Access deployed application with your browser

Now to access the application run a `port-forward` command of the Kubernetes service to your local computer

```bash
kubectl port-forward service/fastdash 8050
```

With your browser open the following URL: `http://localhost:8050`
You should be able to see a web page.

![Screenshot](/assets/images/fastdash.png)

As you can see this is a FastDash application. FastDash is a simple framework to create a web prototypes for macine learning models. You can find more information about FastDash [here](http://fastdash.app)

You can enter the `TEXT` and select `FROM_LANG` and `TO_LANG` and click `Submit` button. The application will send the request to the deployed model and display the result.

> Please consult available languages for your model. You can find the list of available languages [here](https://huggingface.co/transformers/model_doc/t5.html#t5forconditionalgeneration)

4. OPTIONAL: Expose application with the Ingress

Instead of creating a port-forward tunnel to your application you can expose it with the Ingress. 

```bash
kubectl get -f "kubernetes/ingress.yaml"
```

Capture ingress address and open it with your browser

```bash
kubectl get ingress
# Result of the command
# 
# NAME       CLASS     HOSTS   ADDRESS         PORTS   AGE
# fastdash             *       192.168.1.230   80      3m44s
```

### Conclusion

In this tutorial you have successfully packaged T5 model and deployed it to GKE Autopilot Cluster. You have also deployed a FastDash application to access the model.

GKE Autopilot is able to read resource requests from your deployments and automatically provision Kubernetes nodes with correct sizing. You can find more information about GKE Autopilot [here](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)

## Cleanup

Before you delete the GKE Autopilot Cluster you need to delete the Kubernetes resources.

```bash
kubectl delete -f 'kubernetes'
```

Delete the GKE Autopilot Cluster

```bash
gcloud container clusters delete "$GKE_NAME" --region="$LOCATION" --quiet
```

Images stored in the GCR are not automatically deleted. These images has been stored in the `gcr.io/$GOOGLE_CLOUD_PROJECT` repository. You can delete them manually or you can use the [Cloud Build](https://cloud.google.com/build) to automatically delete the images.

Alternatively you will notice GCR has been automatically created GS bucket. If you don't have any other images you can delete this bucket as well.

```bash
gsutil rm -r "gs://artifacts.$GOOGLE_CLOUD_PROJECT.appspot.com/"
```

## See also

* About GKE Autopilot: [Learn more](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)

## Troubleshooting

Here are some common issues you may encounter when deploying the model to GKE Cluster.

### Git LFS

If after cloning the model repository you do not see files stored as LFS objects. 

```bash
cd model/$MODEL_NAME
git lfs env

# optionally install git-lfs
# git lfs install

git lfs pull
```

> You can find more information about Git LFS [here](https://git-lfs.github.com/)

### GKE Autopilot

For troubleshooting GKE Autopilot, refer to [Troubleshooting Autopilot clusters](https://cloud.google.com/kubernetes-engine/docs/troubleshooting/troubleshooting-autopilot-clusters).


## TODOs

* [x] Check newer versions of the model T5X and T5_v1.1
* [ ] Check on potential performance metrics GPU vs CPU
* [ ] Check on potential Triton serving instead of TorchServe
* [ ] Check on potential Tensorflow serving instead of TorchServe
* [ ] Check on potential closed book questioning variant
* [ ] Check on potential prometheus integration
* [ ] Check on potential tensorboard integration
