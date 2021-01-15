import os
import glob
import csv
import datetime
import time
import paramiko
import base64
import requests
from requests.auth import HTTPBasicAuth
import ujson
from PIL import Image

from ggt.lib.utils import (
    get_config_val as cfg,
    log_generic,
    generate_session_id,
    whoami
)


from ggt.lib.db import (
    exec_insert,
    exec_update,
    read_row,
    read_rows
)


import ggt.lib.constants as c

session_id = generate_session_id()


def task_process_crl_lab_orders():
    print('\n\n************************************************\n\n')
    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='Begin Processing outbound CRL Lab Orders')

    while True:
        orders = get_orders_ready_to_transmit(100)
        if len(orders) > 0:
            processed_orders = create_outbound_files(orders)
            update_to_with_lab_status(processed_orders)
            print('--------------------------')
        else:
            break

    log_generic(
        type=c.INFO,
        function=whoami(),
        task_session_id=session_id,
        info='End Processing outbound Lab Reports')
    print('\n\n************************************************\n\n')



def create_outbound_files(orders):
    processed_orders = []
    for order in orders:
        if order['sample_collection_location_id'] == 2473:
            try:
                make_api_request(order)
                processed_orders.append(order)

            except Exception as err:
                print(err)
                print('Error generating HL7 for CRL/Order ID:', order['id'])

    return processed_orders


def make_api_request(order):
    payload = {
        "order": {
            "customerId": "54086",
            "reference": order['client_order_number'],
            "barcodeNumber": order['sample_code'],
            "performedByAdult": True,
            "registrationDate": order['date_of_collection'],
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
                            "zip": "75024"
            }
        },
        "labAccount": {
            "client": "CRL",
            "region": "EMCT",
            "ref1": "",
            "ref2": ""
        },
        "recipient": {
            "firstName": order['first_name'],
            "lastName": order['last_name'],
            "birthDate": order['dob'],
            "gender": order['gender'],
            "phone": order['phone_number'].replace('+1', ''),
            "email": '',
            "address": {
                "line1": order['addr1'],
                "line2": order['addr2'],
                "city": order['city'],
                "state": order['st'],
                "zip": order['zip']
            },
            "ethnicity": order['ethnicity'],
            "race": order['race'],
        } 
    }

    '''
    "symptomQuestions": [{
        "question": "Is this the patient's first COVID-19 test?",
        "answer": order['is_first_test']
    },
        {
        "question": "Is the patient employed in healthcare with direct patient contact?",
        "answer": order['is_healthcare_employee']
    },
        {
        "question": "Is the patient exhibiting symptoms as defined by the CDC?",
        "answer": order['is_cdc_symptomatic']
    },
        {
        "question": "When was first sign of symptoms? (Blank if no or unknown)",
        "answer": order['is_cdc_symptomatic']
    },
        {
        "question": "Has the patient been hospalized?|",
        "answer": order['is_hospitalized']
    },
        {
        "question": "Has the patient been hospalized in the ICU?",
        "answer": order['is_in_icu']
    },
        {
        "question": "Does the patient reside in congregate care (nursing home, group home, etc.)?",
        "answer": order['is_congregate_resident']
    },
        {
        "question": "Is the patient pregnant?",
        "answer": order['is_pregnant']
    }
    ]
    '''
    print(ujson.dumps(payload))
    invoke_post(payload)


def invoke_post(payload):
    auth_user = 'WELLHEALTH'
    auth_password = '38cvZtg4v8'
    
    base_url = 'https://api-stage.crlclear.com'
    resource_path = '/order'

    try:
        url = '{}{}'.format(base_url, resource_path)
        auth = HTTPBasicAuth(auth_user, auth_password)
        headers = {}
        r = requests.post(url, auth=auth, headers=headers, json=payload)
        response = r.json()
        print(response)

        if r.status_code == 200 or r.status_code == 201:
            print('success')
        else:
            print('error', r.text)
            json_object = ujson.dumps(payload, indent = 4)   
            print(json_object)  


    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )



def get_orders_ready_to_transmit(limit=100):
    sql = """
        SELECT 
            t.id AS id,
            t.patient_id AS patient_id,
            REPLACE(p.first_name, ',', '') AS first_name,
            REPLACE(p.last_name, ',', '') AS last_name,
            DATE_FORMAT(p.dob, '%Y-%m-%d') AS dob,
            (CASE
                WHEN (p.gender = 'male') THEN 'Male'
                WHEN (p.gender = 'female') THEN 'Female'
                ELSE 'U'
            END) AS gender,
            (CASE
                WHEN (t.sample_collection_start_dt IS NOT NULL) THEN 
                    DATE_FORMAT(CONVERT_TZ(t.sample_collection_start_dt,
                            '+00:00',
                            '-06:00'),
                    '%Y-%m-%d %H:%m:%s.000')
                WHEN (t.sample_collection_end_dt IS NOT NULL) THEN 
                    DATE_FORMAT(CONVERT_TZ(t.sample_collection_end_dt,
                            '+00:00',
                            '-06:00'),
                    '%Y-%m-%d %H:%m:%s.000')
                WHEN (t.pre_ship_label_scan_dt IS NOT NULL) THEN 
                    DATE_FORMAT(CONVERT_TZ(t.pre_ship_label_scan_dt,
                            '+00:00',
                            '-06:00'),
                    '%Y-%m-%d %H:%m:%s.000')
                ELSE DATE_FORMAT(CONVERT_TZ(NOW(),
                            '+00:00',
                            '-06:00'),
                    '%Y-%m-%d %H:%m:%s.000')
            END) AS date_of_collection,
            (CASE
                WHEN (p.race = 'race_american_indian') THEN 'American Indian or Alaska Native'
                WHEN (p.race = 'race_asian') THEN 'Asian'
                WHEN (p.race = 'race_black') THEN 'Black or African-American'
                WHEN (p.race = 'race_hawaiian') THEN 'Native Hawaiian or Other Pacific Islander'
                WHEN (p.race = 'race_other') THEN 'Other Race'
                WHEN (p.race = 'race_white') THEN 'White'
                ELSE 'Unknown/undetermined'
            END) AS race,
            (CASE
                WHEN (p.ethnicity = 'true') THEN 'Hispanic or Latino'
                WHEN (p.ethnicity = 'false') THEN 'Not Hispanic or Latino'
                WHEN (p.ethnicity = 'hispanic_latino_spanish') THEN 'Hispanic or Latino'
                ELSE 'Not Hispanic or Latino'
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
            l.st as test_location_st,
            t.sample_collection_location_id
        FROM
            (((test_samples t
            JOIN patients p ON ((t.patient_id = p.id)))
            JOIN locations l ON ((t.sample_collection_location_id = l.id)))
            JOIN patient_questionnaires q ON ((p.id = q.patient_id)))
        WHERE
            (t.status = 'ready_to_tx')
            AND t.lab_id = 3
        LIMIT {}
            """.format(limit)
    return read_rows(sql,)


def update_to_with_lab_status(orders):
    if len(orders) == 0:
        return

    list_of_ids = []
    for order in orders:
        list_of_ids.append(order['client_order_number'])

    format_strings = ','.join(['%s'] * len(list_of_ids))
    sql = """
        UPDATE test_samples 
        SET 
            status = 'with_lab',
            update_dt = NOW(),
            lab_electronic_submission_dt = NOW()
        WHERE
            id IN (%s)
        """ % format_strings

    exec_update(sql, tuple(list_of_ids))
