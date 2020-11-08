#!/bin/bash

ENV="${1}"

python create_roles.py
python create_permissions.py ${ENV}
python assign_permissions_to_roles.py ${ENV}