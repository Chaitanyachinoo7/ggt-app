#!/bin/bash
echo 🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅🔅
cd "$(dirname "$0")"

set -ex

PARENT_DIR=$(basename "${PWD%/*}")
CURRENT_DIR="${PWD##*/}"

#gcloud config configurations activate ggt-pfe-prod

export PIPENV_IGNORE_VIRTUALENVS=1
pipenv lock --requirements > app/requirements.txt

cp app/ggt/configs/config-TEST.yml app/ggt/configs/config.yml
pytest -W ignore -s app/tests/
