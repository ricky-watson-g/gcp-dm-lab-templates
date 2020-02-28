#!/bin/bash 

set -x

function raise_error {
  echo "####################################################"
  echo "####################################################"
  echo "####################################################"
  echo "####################################################"
  echo "Failing deployment due to error in: $1"
  echo "####################################################"
  echo "####################################################"
  echo "####################################################"
  echo "####################################################"
  gcloud beta runtime-config configs variables set \
           failure/jumphost-waiter \
           failure --config-name jumphost-installer-config
}

### Save user
export QWIKLABS_USER=$1

### Set Zone
gcloud config set compute/zone us-east1-d

git clone https://github.com/GoogleCloudPlatform/continuous-deployment-on-kubernetes.git

cd continuous-deployment-on-kubernetes


### Create Cluster
gcloud container clusters create jenkins-cd --num-nodes 2 --machine-type n1-standard-2 --scopes "https://www.googleapis.com/auth/source.read_write,cloud-platform"
sleep 15

gcloud container clusters get-credentials jenkins-cd

wget https://storage.googleapis.com/kubernetes-helm/helm-v2.14.1-linux-amd64.tar.gz

tar zxfv helm-v2.14.1-linux-amd64.tar.gz
cp linux-amd64/helm .

kubectl create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=$(gcloud config get-value account)

kubectl create serviceaccount tiller --namespace kube-system

kubectl create clusterrolebinding tiller-admin-binding --clusterrole=cluster-admin --serviceaccount=kube-system:tiller

./helm init --service-account=tiller

./helm update

./helm install -n cd stable/jenkins -f jenkins/values.yaml --version 1.2.2 --wait

kubectl create clusterrolebinding jenkins-deploy --clusterrole=cluster-admin --serviceaccount=default:cd-jenkins

export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/component=jenkins-master" -l "app.kubernetes.io/instance=cd" -o jsonpath="{.items[0].metadata.name}")
kubectl port-forward $POD_NAME 8080:8080 >> /dev/null &

JENKINS_PASSWORD=$(kubectl get secret cd-jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode)




### Create Service Account
gcloud iam service-accounts create spinnaker-account --display-name -account
sleep 15
export PROJECT=$(gcloud projects list --format='value(name)')
export SA_EMAIL=$(gcloud iam service-accounts list --filter="displayName:spinnaker-account" --format='value(email)')

gcloud config set project $PROJECT
gcloud projects add-iam-policy-binding $PROJECT  --role roles/storage.admin --member serviceAccount:$SA_EMAIL
gcloud iam service-accounts keys create spinnaker-sa.json --iam-account $SA_EMAIL

### Pub/Sub
gcloud pubsub topics create projects/$PROJECT/topics/gcr
gcloud pubsub subscriptions create gcr-triggers --topic projects/${PROJECT}/topics/gcr
gcloud beta pubsub subscriptions add-iam-policy-binding gcr-triggers --role roles/pubsub.subscriber --member serviceAccount:$SA_EMAIL

### Helm
echo Helm...
wget https://storage.googleapis.com/kubernetes-helm/helm-v2.10.0-linux-amd64.tar.gz
tar zxfv helm-v2.10.0-linux-amd64.tar.gz
cp linux-amd64/helm .
kubectl create clusterrolebinding user-admin-binding --clusterrole=cluster-admin --user=$QWIKLABS_USER
sleep 3
kubectl create serviceaccount tiller --namespace kube-system
sleep 3
kubectl create clusterrolebinding tiller-admin-binding --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
sleep 3
kubectl create clusterrolebinding --clusterrole=cluster-admin --serviceaccount=default:default spinnaker-admin
sleep 60
./helm init --service-account=tiller
if [ $? -ne 0 ]
then
  raise_error "helm init failed..."
  exit 1
fi

sleep 1
./helm repo update
sleep 3
export BUCKET=$PROJECT-spinnaker-config
gsutil mb -c regional -l us-central1 gs://$BUCKET
export SA_JSON=$(cat spinnaker-sa.json)

cat > spinnaker-config.yaml <<EOF
gcs:
  enabled: true
  bucket: $BUCKET
  project: $PROJECT
  jsonKey: '$SA_JSON'

dockerRegistries:
- name: gcr
  address: https://gcr.io
  username: _json_key
  password: '$SA_JSON'
  email: 1234@5678.com

# Disable minio as the default storage backend
minio:
  enabled: false

# Configure Spinnaker to enable GCP services
halyard:
  spinnakerVersion: 1.10.2
  image:
    tag: 1.12.0
  additionalScripts:
    create: true
    data:
      enable_gcs_artifacts.sh: |-
        \$HAL_COMMAND config artifact gcs account add gcs-$PROJECT --json-path /opt/gcs/key.json
        \$HAL_COMMAND config artifact gcs enable
      enable_pubsub_triggers.sh: |-
        \$HAL_COMMAND config pubsub google enable
        \$HAL_COMMAND config pubsub google subscription add gcr-triggers \
          --subscription-name gcr-triggers \
          --json-path /opt/gcs/key.json \
          --project $PROJECT \
          --message-format GCR
EOF
COUNT=0
echo Helm Install...
./helm install -n cd stable/spinnaker -f spinnaker-config.yaml --timeout 600 --version 1.1.6 --wait
while [ $? -ne 0 ]
do 
  sleep 30
  ./helm install -n cd stable/spinnaker -f spinnaker-config.yaml --timeout 600 --version 1.1.6 --wait
  COUNT=$((COUNT+1))
  if [ $COUNT -gt 3 ]
  then
    raise_error "helm install failed after 3 retries..."
    exit 1
  fi
done

### Software
wget https://gke-spinnaker.storage.googleapis.com/sample-app-v2.tgz
tar xzfv sample-app-v2.tgz
cd sample-app
git config --global user.email "$(gcloud config get-value core/account)"
git config --global user.name "student"
git init
sed -i s/PROJECT/$PROJECT/g k8s/deployments/*
git add .
git commit -m "Initial commit"
gcloud source repos create sample-app
git config credential.helper gcloud.sh
git remote add origin https://source.developers.google.com/p/$PROJECT/r/sample-app
git push origin master
gcloud alpha builds triggers create cloud-source-repositories --repo=sample-app --tag-pattern="v.*" --build-config="cloudbuild.yaml" --description="sample-app-tags"
gsutil mb -l us-central1 gs://$PROJECT-kubernetes-manifests
gsutil versioning set on gs://$PROJECT-kubernetes-manifests
git add .
git commit -a -m "Set project ID"
git tag v1.0.0
git push --tags
sleep 3
gcloud alpha builds triggers run sample-app-tags --tag v1.0.0

export DECK_POD=$(kubectl get pods --namespace default -l "cluster=spin-deck" -o jsonpath="{.items[0].metadata.name}")

STATUS=$(kubectl describe pod $DECK_POD | grep Status: | tr -s " " | cut -f2 -d" ")
COUNT=0
while [ "$STATUS" != "Running" ]
do
  sleep 10
  STATUS=$(kubectl describe pod $DECK_POD | grep Status: | tr -s " " | cut -f2 -d" ")
  COUNT=$((COUNT+1))
  if [ $COUNT -gt 10 ]
  then
    raise_error "deck pod stuck in Pending after 10 retries..."
    exit 1
  fi
done

kubectl port-forward --namespace default $DECK_POD 8080:9000 >> /dev/null &

curl -LO https://storage.googleapis.com/spinnaker-artifacts/spin/1.6.0/linux/amd64/spin
chmod +x spin
curl -I http://localhost:8080/gate | grep HTTP
COUNT=0
while [ $(curl -I http://localhost:8080/gate | grep -c 302) -ne 1 ]; 
do
  curl -I http://localhost:8080/gate | grep HTTP
  sleep 30
  COUNT=$((COUNT+1))
  if [ $COUNT -gt 15 ]
  then
    raise_error "deck failed to become available after 15 retries..."
    exit 1
  fi
done
curl -I http://localhost:8080/gate | grep HTTP
./spin application save --application-name sample \
                        --owner-email "$(gcloud config get-value core/account)" \
                        --cloud-providers kubernetes \
                        --gate-endpoint http://localhost:8080/gate
export PROJECT=$(gcloud info --format='value(config.project)')
sed s/PROJECT/$PROJECT/g spinnaker/pipeline-deploy.json > pipeline.json
./spin pipeline save --gate-endpoint http://localhost:8080/gate -f pipeline.json


gcloud beta runtime-config configs variables set \
          success/jumphost-waiter \
          success --config-name jumphost-installer-config