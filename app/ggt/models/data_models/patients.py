from typing import List

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami, generate_token, get_user_token_from_jwt
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    replica_read_row,
    replica_read_rows
)

from ggt.models.data_models.data_types import (
    GgtPatient,
    PatientUpfrontPayment,
    ServicePayment,
)
########################################################################################################
# [Public] functions
########################################################################################################


def create_patient_record(patient):
    try:
        sql = """
            INSERT INTO 
                patients (
                    first_name, 
                    middle_name, 
                    last_name, 
                    addr1, 
                    city, 
                    st, 
                    zip,
                    gender, 
                    height_ft, 
                    weight_lb, 
                    ethnicity, 
                    race,  
                    dob, 
                    phone_number, 
                    phone_number_verified, 
                    email, 
                    token,
                    result_token,
                    token_expire,
                    country
                )
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                DATE_ADD(NOW(), interval 10 minute), %s)
        """

        vals = (
            patient.first_name, 
            patient.middle_name, 
            patient.last_name, 
            patient.addr1,
            patient.city, 
            patient.st, 
            patient.zip, 
            patient.gender, 
            patient.height_ft,
            patient.weight_lb, 
            patient.ethnicity, 
            patient.race,  
            patient.dob,
            patient.phone_number, 
            patient.phone_number_verified, 
            patient.email,
            patient.token,
            patient.token,
            patient.country
        )

        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR, 
            vals=vals, 
            patient=patient,
            function=whoami(), 
            error=err
        )
        return None


def add_to_ggd_waiting_queue(patient_id):
    try:
        sql = """
            INSERT INTO 
                ggd_waiting_list (patient_id)
            VALUES (%s)
        """
        vals = (patient_id,)
        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            vals=vals,
            patient=patient_id,
            function=whoami(),
            error=err
        )
        return None


def create_pre_registration(patient_id):
    try:
        sql = """
            INSERT INTO 
                vax_pre_registrations (patient_id)
            VALUES (%s)
        """
        vals = (patient_id,)
        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            vals=vals,
            patient=patient_id,
            function=whoami(),
            error=err
        )
        return None


def get_existing_patients(phone_number="", first_name="", last_name="", dob="", token=""):

    where_statement = "phone_number_verified = 1 AND token not like 'NOVERIFY%'"
    if phone_number != "":
        where_statement = "{} AND phone_number = '{}'".format(where_statement, phone_number)
    if first_name != "":
        where_statement = "{} AND first_name = '{}'".format(where_statement, first_name)
    if last_name != "":
        where_statement = "{} AND last_name = '{}'".format(where_statement, last_name)
    if dob != "":
        where_statement = "{} AND dob = '{}'".format(where_statement, dob)
    if token != "":
        where_statement = "{} AND token = '{}'".format(where_statement, token)
    try:
        sql = """SELECT 
                        *
                    FROM
                        patients
                    WHERE
                        {};""".format(where_statement)
        return replica_read_row(sql)

    except Exception as err:
        log_generic(
            type=ERROR,
            phone_number=phone_number,
            function=whoami(),
            error=err
        )
        return None


def get_existing_patient_questionnaire(patient_id):
    try:
        sql = """SELECT 
                        *
                    FROM
                        patient_questionnaires
                    WHERE
                        patient_id = %s;"""
        vals = (patient_id,)
        return replica_read_row(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            vals=vals,
            patient_id=patient_id,
            function=whoami(),
            error=err
        )
        return None
#
#
# def is_available_slot(email, dob):
#     try:
#         sql = """SELECT
#                         *
#                     FROM
#                         temp_selected_patients
#                     WHERE
#                         email = %s AND dob = %s;"""
#         vals = (email, dob)
#         return replica_read_row(sql, vals)
#
#     except Exception as err:
#         log_generic(
#             type=ERROR,
#             vals=vals,
#             email=email,
#             dob=dob,
#             function=whoami(),
#             error=err
#         )
#         return None


def is_un_available_slot(token):
    u_token = get_user_token_from_jwt(token)
    if u_token is None:
        return {"status": "Invalid token"}
    try:
        sql = """SELECT 
                        *
                    FROM
                        used_tokens
                    WHERE
                        token = %s;"""
        vals = (u_token,)
        return replica_read_row(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            vals=vals,
            token=token,
            function=whoami(),
            error=err
        )
        return {"status": "Invalid token"}

#
# def lock_slot(id):
#     try:
#         sql = """UPDATE
#                         temp_selected_patients
#                     SET
#                     is_available = False
#                     WHERE id = %s;"""
#         vals = (id, )
#         return exec_update(sql, vals)
#
#     except Exception as err:
#         log_generic(
#             type=ERROR,
#             vals=vals,
#             function=whoami(),
#             error=err
#         )
#         return None


def lock_slot(token, appointment_1_id, appointment_2_id):
    try:
        u_token = get_user_token_from_jwt(token)
        if u_token is None:
            return None
        sql = """INSERT INTO
                        used_tokens
                    (token, appointment_1_id, appointment_2_id)
                    VALUES (%s, %s, %s)"""
        vals = (u_token, appointment_1_id, appointment_2_id,)
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            vals=vals,
            function=whoami(),
            error=err
        )
        return None


def unlock_patient_info_patients(phone_number):
    try:
        result_token = generate_token()
        sql = """UPDATE patients 
                    SET 
                        result_token = %s,
                        token_expire = DATE_ADD(NOW(), interval 10 minute)
                    WHERE
                        phone_number = %s AND token NOT LIKE 'NOVERIFY%'"""
        vals = (result_token, phone_number)
        if exec_update(sql, vals):
            return result_token
        else:
            return None
    except Exception as err:
        log_generic(
            type=ERROR,
            vals=vals,
            phone_number=phone_number,
            function=whoami(),
            error=err
        )
        return None


def get_insurance_record_by_id(patient_id):
    try:
        sql = """SELECT * FROM
                       patient_insurance_details 
                   WHERE patient_id = %s
               """
        vals = (patient_id, )
        return replica_read_row(sql, vals)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def create_patient_insurance_record(booking_req):
    try:
        sql = """INSERT INTO 
                       patient_insurance_details 
                       (
                       `patient_id`,
                       `relationship`,
                       `payer`,
                       `member_id`,
                       `group_no`,
                       `level`
                       )
                   VALUES (%s, %s ,%s, %s, %s, %s)
               """
        vals = (booking_req.patient_id, booking_req.insurance_relationship,
                booking_req.insurance_payer, booking_req.insurance_member_id,
                booking_req.insurance_group_no, booking_req.insurance_level)

        return exec_update(sql, vals)
    except Exception as err:
        log_generic(
            type=ERROR,
            vals=vals,
            function=whoami(),
            error=err
        )
        return None


def get_patient(patient_id):
    try:
        sql = """
            SELECT 
                id, 
                first_name, 
                middle_name, 
                last_name, 
                dob, 
                token 
            FROM 
                patients 
            WHERE 
                id=%s 
            LIMIT 1
        """
        vals = (patient_id,)
        row = read_row(sql, vals)

        patient = GgtPatient()
        patient.id = row['id']
        patient.first_name = row['first_name']
        patient.middle_name = row['middle_name']
        patient.last_name = row['last_name']
        patient.dob = row['dob']
        patient.token = row['token']

        log_generic(
            type=INFO, 
            patient_id=patient_id,
            row=row, 
            function=whoami()
        )

        return (patient)

    except Exception as err:
        log_generic(
            type=ERROR, 
            id=id,
            function=whoami(), 
            error=err
        )
        return None


def get_patient_by_token(token, expect_no_match=False):
    try:
        sql = """
            SELECT 
                id, 
                first_name, 
                middle_name, 
                last_name, 
                dob, 
                token 
            FROM 
                patients 
            WHERE 
                token=%s 
            LIMIT 1
        """
        vals = (token,)
        row = replica_read_row(sql, vals)

        #When checking Table for duplicates, Null is the expected result
        if expect_no_match and row is None:
            return None

        log_generic(
            type=INFO,
            token=token,
            function=whoami()
        )

        patient = GgtPatient()
        patient.id = row['id']
        patient.first_name = row['first_name']
        patient.middle_name = row['middle_name']
        patient.last_name = row['last_name']
        patient.dob = row['dob']
        patient.token = row['token']
        return (patient)

    except Exception as err:
        log_generic(
            type=ERROR,
            id=id,
            function=whoami(),
            error=err
        )
        return None


def get_patient_upfront_payment(service_codes: List[str]):
    try:
        # Add quotes around service_codes to be injected to sql
        quoted_service_code = map(lambda code: "'" + code + "'", service_codes)
        # Join quoted codes by ','
        service_codes_in = ",".join(quoted_service_code)
        sql = """
            SELECT 
                selfpay_amount,
                service_code,
                service_name,
                currency
            FROM
                services_catalog
            WHERE
                service_code in ({})
        """.format(service_codes_in)

        rows = replica_read_rows(sql)

        if not rows:
            return None

        patient_payments = []

        # Iterate over rows and generate service payment object
        for row in rows:
            service_payment = ServicePayment()
            service_payment.service_code = row['service_code']
            service_payment.service_name = row['service_name']
            service_payment.selfpay_amount = row['selfpay_amount']
            service_payment.currency = row['currency']

            patient_payments.append(service_payment)

        return patient_payments

    except Exception as err:
        log_generic(
            type=ERROR,
            id=id,
            function=whoami(),
            error=err
        )
        return None


########################################################################################################
# [Protected] functions
########################################################################################################
