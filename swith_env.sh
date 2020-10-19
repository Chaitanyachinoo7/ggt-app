#!/bin/bash
cd "$(dirname "$0")"

set -ex

PARENT_DIR=$(basename "${PWD%/*}")
CURRENT_DIR="${PWD##*/}"
ENV="${1}"
PROJECT_ID='ggt-pfe-'${ENV}
SERVICE_NAME='ggt-pfe-services'
REGION='us-central1'

gcloud config configurations activate ggt-pfe-${ENV}

pipenv lock --requirements > app/requirements.txt

cp app/ggt/configs/config-${ENV}.yml app/ggt/configs/config.yml
cp app/ggt/configs/log-config-${ENV}.yml app/ggt/configs/log-config.yml
cp app/ggt/configs/gcp-service-account-${ENV}.json app/ggt/configs/gcp-service-account.json
