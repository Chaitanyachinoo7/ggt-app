from ggt.tasks.lab_integration.outbound.hl7 import HL7
from ggt.tasks.lab_integration import utils
from ggt.lib.adapters.s3_adapter import write_text_file

from ggt.lib.utils import (
    get_config_val as cfg,
    print_header,
    print_ok1,
    print_warning,
    print_error
)

from ggt.lib.db import (
    exec_update,
    read_rows
)

from requests.auth import HTTPBasicAuth
import requests
import os


outbound_file_prefix = cfg('lab_integrations.outbound_file_prefix')
crl_auth_user = cfg('lab_integrations.CRL.api_username')
crl_auth_password = cfg('lab_integrations.CRL.api_password')
crl_api_url = cfg('lab_integrations.CRL.api_url')
bucket_name = cfg('lab_integrations.s3_bucket')


CRL_RACE_MAP = {
    '1002-5': "American Indian or Alaska Native",
    '2028-9': "Asian",
    '2054-5': "Black or African-American",
    '2076-8': "Native Hawaiian or Other Pacific Islander",
    '2131-1': "Other Race",
    '2106-3': "White",
    'Unknown': "Unknown/undetermined"
}

CRL_ETHNICITY_MAP = {
    "H": "Hispanic or Latino",
    "N": "Not Hispanic or Latino",
    "U": "Unknown"
}

CRL_GENDER_MAP = {
    "M": "Male",
    "F": "Female",
    "U": "Other"
}


def _get_crl_api_payload(order):
    """
    Generates the CRL API payload given the order details
    """

    dob = order["dob"]
    dob = "{}-{}-{}".format(dob[:4], dob[4:6], dob[6:])

    race = CRL_RACE_MAP.get(order["race"], "Unknown/undetermined")
    ethnicity = CRL_ETHNICITY_MAP.get(order["ethnicity"], "Unknown")
    gender = CRL_GENDER_MAP.get(order["gender"], "Other")

    crl_payload = {
        "order": {
            "customerId": "54086",
            "reference": order["client_order_number"],
            "barcodeNumber": order["sample_code"],
            "performedByAdult": True,
            "registrationDate": order["date_of_collection"],
            "testCode": "U847",
            "specimenType": "ORAL-OM-505",
            "physicianFirstName": "Samad",
            "physicianLastName": "Khan",
            "physicianPhone": "4697892595",
            "physicianAddress": {
                        "line1": "6827 Communications Parkway",
                        "line2": "",
                        "city": "Plano",
                        "state": "TX",
                        "zip": "75024",
            },
        },
        "labAccount": {"client": "ZSK", "region": "EMCW", "ref1": "", "ref2": ""},
        "recipient": {
            "firstName": order["first_name"],
            "lastName": order["last_name"],
            "birthDate": dob,
            "gender": gender,
            "phone": order["phone_number"].replace("+1", ""),
            "email": "",
            "address": {
                "line1": order["addr1"],
                "line2": order["addr2"],
                "city": order["city"],
                "state": order["st"],
                "zip": order["zip"],
            },
            "ethnicity": ethnicity,
            "race": race,
            "guardianfirstName": "ON FILE WITH",
            "guardianlastName": "WELLHEALTH",
            "guardianPhone": "8778378461",
            "guardianRelationship": "Care giver",
        }
    }

    return crl_payload


def get_orders_ready_to_transmit(limit=100):
    """
    Gets all the orders from the database which are 'ready_to_tx'
    """

    sql = """
        SELECT
            t.id AS id,
            t.patient_id AS patient_id,
            REPLACE(p.first_name, ',', '') AS first_name,
            REPLACE(p.last_name, ',', '') AS last_name,
            DATE_FORMAT(p.dob, '%Y%m%d') AS dob,
            (CASE
                WHEN (p.gender = 'male') THEN 'M'
                WHEN (p.gender = 'female') THEN 'F'
                ELSE 'U'
            END) AS gender,
            (CASE
                WHEN
                    (t.sample_collection_start_dt IS NOT NULL)
                THEN
                    DATE_FORMAT(CONVERT_TZ(t.sample_collection_start_dt,
                                    '+00:00',
                                    '-06:00'),
                            '%Y%m%d%H%m%s')
                WHEN
                    (t.sample_collection_end_dt IS NOT NULL)
                THEN
                    DATE_FORMAT(CONVERT_TZ(t.sample_collection_end_dt,
                                    '+00:00',
                                    '-06:00'),
                            '%Y%m%d%H%m%s')
                WHEN
                    (t.pre_ship_label_scan_dt IS NOT NULL)
                THEN
                    DATE_FORMAT(CONVERT_TZ(t.pre_ship_label_scan_dt,
                                    '+00:00',
                                    '-06:00'),
                            '%Y%m%d%H%m%s')
                ELSE DATE_FORMAT(CONVERT_TZ(NOW(), '+00:00', '-06:00'),
                        '%Y%m%d%H%m%s')
            END) AS date_of_collection,
            (CASE
                WHEN (p.race = 'race_american_indian') THEN '1002-5'
                WHEN (p.race = 'race_asian') THEN '2028-9'
                WHEN (p.race = 'race_black') THEN '2054-5'
                WHEN (p.race = 'race_hawaiian') THEN '2076-8'
                WHEN (p.race = 'race_other') THEN '2131-1'
                WHEN (p.race = 'race_white') THEN '2106-3'
                ELSE 'Unknown'
            END) AS race,
            (CASE
                WHEN (p.ethnicity = 'true') THEN 'H'
                WHEN (p.ethnicity = 'false') THEN 'N'
                WHEN (p.ethnicity = 'hispanic_latino_spanish') THEN 'H'
                ELSE 'U'
            END) AS ethnicity,
            REPLACE(p.addr1, ',', '') AS addr1,
            (CASE
                WHEN ISNULL(p.addr2) THEN ''
                ELSE REPLACE(p.addr2, ',', '')
            END) AS addr2,
            REPLACE(p.city, ',', '') AS city,
            REPLACE(p.st, ',', '') AS st,
            REPLACE(p.zip, ',', '') AS zip,
            p.phone_number AS phone_number,
            (CASE
                WHEN (l.billing_type = 'insurance') THEN 'WELLHLD'
                ELSE 'WELLHLTX'
            END) AS client_site_code,
            (CASE
                WHEN (l.billing_type = 'insurance') THEN '1780944496'
                ELSE '22244887999'
            END) AS physician_npi,
            (CASE
                WHEN
                    ((l.billing_type = 'insurance')
                        AND (q.has_insurance_photo = 1))
                THEN
                    'DB'
                WHEN
                    ((l.billing_type = 'insurance')
                        AND (q.has_insurance_photo <> 1))
                THEN
                    'SP'
                ELSE 'CB'
            END) AS bill,
            t.id AS client_order_number,
            t.vial_id AS sample_code,
            (CASE
                WHEN (l.st = 'SC') THEN 'Pod 1 South Carolina'
                ELSE ''
            END) AS collected_by,
            'Respiratory' AS sample_type,
            (CASE
                WHEN (l.test_type_offered = 'oral') THEN 'ORAL SWAB'
                WHEN (l.test_type_offered = 'oral_fluid') THEN 'ORAL FLUID'
                ELSE 'NASOPHARYNGEAL SWAB'
            END) AS sample_source,
            'RESPI507' AS panel_code,
            'COVID-19 Coronavirus (SARS-CoV-2)' AS panel_name,
            'Unknown' AS is_first_test,
            'Unknown' AS is_healthcare_employee,
            'Unknown' AS is_cdc_symptomatic,
            'Unknown' AS is_hospitalized,
            'Unknown' AS is_in_icu,
            'Unknown' AS is_congregate_resident,
            'Unknown' AS is_pregnant,
            l.st AS test_location_st,
            l.addr1 AS test_location_addr,
            l.city AS test_location_city,
            l.zip as test_location_zip,
            l.country as test_location_country,
            t.sample_collection_location_id,
            t.lab_id,
            DATE_FORMAT(CONVERT_TZ(NOW(), '+00:00', '-06:00'),
                        '%Y%m%d%H%m%s') as today_dt
        FROM
            (((test_samples t
            JOIN patients p ON (t.patient_id = p.id))
            JOIN locations l ON (t.sample_collection_location_id = l.id))
            JOIN patient_questionnaires q ON (q.id = t.patient_questionnaire_id))
        WHERE
            (t.status = 'ready_to_tx')
            AND t.vial_id IS NOT NULL
        LIMIT {}
            """.format(limit)
    return read_rows(sql,)


def create_outbound_requests(orders):
    """
    Creates outbound requests to the corresponding labs for all the pending orders
    """

    processed = []
    for order in orders:

        # Post test data as an API call for CRL labs
        if order['lab_id'] == 3:
            result, *metadata = post_to_crl(order)

            if not result:
                msg = "ERROR: Unable to POST to CRL labs API. GGT-ORDER: {0}".format(order[
                                                                                     'id'])
                print_error(msg)
                utils.log_error(order_id=order['id'], lab_id=order[
                                'lab_id'], metadata=metadata, msg=msg, direction="outbound")
                continue

            processed.append(order)
            continue

        # for all other labs, generate hl7 file and place it in s3
        hl7_util = HL7(order.copy())
        result, hl7_string, *metadata = hl7_util.generate_string()

        if not result:
            msg = "ERROR: Unable to generate HL7 file. GGT-ORDER: {0}".format(order[
                                                                              'id'])
            print_error(msg)
            utils.log_error(order_id=order['id'], lab_id=order[
                            'lab_id'], metadata=metadata, msg=msg, direction="outbound")
            continue

        filename = "{}-{}.hl7".format(outbound_file_prefix, order['id'])
        result, *metadata = create_s3_file(
            order=order, name=filename, content=hl7_string, lab_id=order['lab_id'])

        if not result:
            msg = "ERROR: Unable to write HL7 file to S3. GGT-ORDER: {0}".format(order[
                                                                                 'id'])
            print_error(msg)
            utils.log_error(order_id=order['id'], lab_id=order[
                            'lab_id'], metadata=metadata, msg=msg, direction="outbound")
            continue

        processed.append(order)

    return processed


def create_s3_file(order, name, content, lab_id):
    """
    Pushed the hl7 file to s3 under the folder for the lab
    """
    try:
        content = content.encode("utf-8").decode('utf-8', 'ignore')

        if lab_id == 2 or str(order['sample_code']).startswith('MAWD'):
            path = utils.lab_map[2]["outbound_path"]

        remaining_labs = list(utils.lab_map.keys())
        remaining_labs.remove(2)

        if lab_id in remaining_labs:
            path = utils.lab_map[lab_id]["outbound_path"]

        full_path = os.path.join(path, name)

        if write_text_file(bucket_name, full_path, content):
            return True, None

        return False, None

    except Exception as err:
        return False, str(err)


def post_to_crl(order):
    """
    Makes a POST API call to CRL lab's server to send patient data
    """

    try:
        auth = HTTPBasicAuth(crl_auth_user, crl_auth_password)
        headers = {}
        r = requests.post(crl_api_url, auth=auth,
                          headers=headers, json=_get_crl_api_payload(order))
        response = r.json()

        if r.status_code == 200 or r.status_code == 201:
            return True, None
        else:
            print_error('ERROR: ' + str(r.text))
            return False, r.text

    except Exception as err:
        return False, str(err)


def update_to_with_lab_status(orders):
    """
    Updates the status of test samples to 'with_lab'
    """

    if len(orders) == 0:
        return

    order_ids = tuple(order['client_order_number'] for order in orders)
    format_strings = ','.join(['%s'] * len(order_ids))

    sql = """
        UPDATE test_samples
        SET
            status = 'with_lab',
            update_dt = NOW(),
            lab_electronic_submission_dt = NOW()
        WHERE
            id IN (%s)
        """ % format_strings

    exec_update(sql, order_ids)
