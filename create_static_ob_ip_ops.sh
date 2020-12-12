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
IP_RANGE='10.9.0.0/28'

gcloud config configurations activate ggt-ops-${ENV}

# CREATING VPC CONNECTOR
gcloud components update
gcloud services enable vpcaccess.googleapis.com
gcloud compute networks vpc-access connectors create vpc-connector-${ENV} \
--network ${VPC} \
--region ${REGION} \
--range ${IP_RANGE}

# CREATING NAT
gcloud compute networks list
gcloud compute routers create router-${ENV} \
  --network=${VPC} \
  --region=${REGION}
gcloud compute addresses create origin-ip-${ENV} --region=${REGION}
gcloud compute routers nats create nat-${ENV} \
  --router=router-${ENV} \
  --region=${REGION} \
  --nat-all-subnet-ip-ranges \
  --nat-external-ip-pool=origin-ip-${ENV}