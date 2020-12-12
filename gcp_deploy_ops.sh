#!/bin/bash
cd "$(dirname "$0")"

set -ex

PARENT_DIR=$(basename "${PWD%/*}")
CURRENT_DIR="${PWD##*/}"
ENV="${1}"
PROJECT_ID='ggt-ops-'${ENV}
SERVICE_NAME='ggt-ops-services'
REGION='us-central1'
VPC='default'

gcloud config configurations activate ggt-ops-${ENV}

pipenv lock --requirements > app/requirements.txt

cp app/ggt/configs/config-${ENV}.yml app/ggt/configs/config.yml
cp app/ggt/configs/log-config-${ENV}.yml app/ggt/configs/log-config.yml
cp app/ggt/configs/gcp-service-account-ops-${ENV}.json app/ggt/configs/gcp-service-account.json
cp app/ggt/configs/buildconfigs/cloudbuild-ops-${ENV}.yml app/ggt/configs/buildconfigs/cloudbuild.yml

#TO build docker image locally and push
#docker build -t gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${TAG} -t gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest .
#docker tag ${SERVICE_NAME} gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest
#docker push gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest

#build and deploy all in GCP
#gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}
gcloud builds submit --config app/ggt/configs/buildconfigs/cloudbuild.yml .
#gcloud run deploy --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} --platform managed  --allow-unauthenticated --region ${REGION} ${SERVICE_NAME}
#gcloud run deploy --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} --platform managed  --allow-unauthenticated --region ${REGION} ${SERVICE_NAME}

gcloud beta run deploy ${SERVICE_NAME} --image=gcr.io/${PROJECT_ID}/${SERVICE_NAME} --vpc-connector=vpc-connector-${ENV}  --vpc-egress=all --platform=managed  --allow-unauthenticated --region=${REGION}
#gcloud run services update-traffic ${SERVICE_NAME} --to-latest
