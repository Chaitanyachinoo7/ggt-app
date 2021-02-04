#!/bin/bash
echo 🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅
cd "$(dirname "$0")"

set -ex

PARENT_DIR=$(basename "${PWD%/*}")
CURRENT_DIR="${PWD##*/}"

PROJECT_ID='ggt-pfe-prod'
SERVICE_NAME='ggt-pfe-services'
REGION='us-central1'

gcloud config configurations activate ggt-pfe-prod

export PIPENV_IGNORE_VIRTUALENVS=1
pipenv lock --requirements > app/requirements.txt

cp app/ggt/configs/config-LOCAL-PROD.yml app/ggt/configs/config.yml
cp app/ggt/configs/log-config-prod.yml app/ggt/configs/log-config.yml
cp app/ggt/configs/gcp-service-account-prod.json app/ggt/configs/gcp-service-account.json
cp app/ggt/configs/buildconfigs/cloudbuild-prod.yml app/ggt/configs/buildconfigs/config.yml
