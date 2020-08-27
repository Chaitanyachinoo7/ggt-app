#!/bin/bash
cd "$(dirname "$0")"

set -ex

PARENT_DIR=$(basename "${PWD%/*}")
CURRENT_DIR="${PWD##*/}"
ENV="${1}"
PROJECT_ID='ggt-pfe-'${ENV}
SERVICE_NAME='ggt-pfe-services'
REGION='us-central1'


# gcloud config configurations activate ggt-pfe-${ENV}

pipenv lock --requirements > app/requirements.txt

cp app/ggt/configs/config-${ENV}.yml app/ggt/configs/config.yml
#TO build docker image locally and push
#docker build -t gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${TAG} -t gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest .
#docker tag ${SERVICE_NAME} gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest
#docker push gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest

#build and deploy all in GCP
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}
gcloud run deploy --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} --platform managed  --allow-unauthenticated --region ${REGION} ${SERVICE_NAME} 


gcloud run services update-traffic --to-revisions=LATEST=100
gcloud run services update-traffic ${SERVICE_NAME} --to-revisions=LATEST=100