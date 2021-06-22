from datetime import datetime

import ggt.lib.constants as c
from ggt.lib.utils import (
    log_generic,
    whoami)

from ggt.models.data_models.lab import (
    lab_status_update,
    get_verification_level_from_patient_id
)
from ggt.lib.utils import (
    get_config_val as cfg,
    generate_otp,
    generate_token,
    validate_phone_number_format,
    log_generic,
    whoami,
    get_translated_message, is_international
)
import boto3

########################################################################################################
# [Public] functions
########################################################################################################

def bp_lab_status_update(lab_status_update_request):
    try:
        return lab_status_update(lab_status_update_request)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )

def bp_get_vaccine_status(query):
    try:
        patient_id = __get_patient_id(query)
        certs = get_verification_level_from_patient_id(patient_id)
        if("COVID_19_VACCINE_JNJ" not in certs[0]['service_code'] and certs[0]['verification_level'] > 1 and certs[1]['verification_level'] > 1
        and certs[0]['rejected'] == 0 and certs[1]['rejected'] == 0):
            return {
                "fully_vaccinated": True
            }
        elif("COVID_19_VACCINE_JNJ" in certs[0]['service_code'] and certs[0]['verification_level'] > 1 and certs[0]['rejected'] == 0):
            return {
                "fully_vaccinated": True
            }
        return {
            "fully_vaccinated": False
        }

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )



def __get_patient_id(query):
    try:
        boto_client = boto3.client(
            'kms',
            aws_access_key_id=cfg('aws.access_key_id'),
            aws_secret_access_key=cfg('aws.secret_access_key'),
            region_name='us-east-2'
        )
        print(query)
        query = query.encode('utf-8')
        from base64 import b64encode, decodebytes
        print(decodebytes(query))
        response = boto_client.decrypt(CiphertextBlob=decodebytes(query))
        print(response)
        print(response['Plaintext'].decode('utf-8'))
        return response['Plaintext'].decode('utf-8')
    except Exception as err:
        log_generic(
            type=c.ERROR,
            query=query,
            function=whoami(),
            error=err
        )