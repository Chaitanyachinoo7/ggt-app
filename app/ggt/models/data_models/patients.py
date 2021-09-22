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


def update_patient_record(patient, patient_id):
    try:
        sql = """
            UPDATE patients SET
                    middle_name = %s, 
                    addr1 = %s, 
                    city = %s, 
                    st = %s, 
                    zip = %s,
                    gender = %s, 
                    height_ft = %s, 
                    weight_lb = %s, 
                    ethnicity = %s, 
                    race = %s,  
                    country = %s
            WHERE
                    id = %s
        """

        vals = (
            patient.middle_name,
            patient.addr1,
            patient.city,
            patient.st,
            patient.zip,
            patient.gender,
            patient.height_ft,
            patient.weight_lb,
            patient.ethnicity,
            patient.race,
            patient.country,
            patient_id
        )
        return exec_update(sql, vals)

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


def create_pre_registration(patient_id, patient_questionnaire_id, group_code):
    try:
        sql = """
            INSERT INTO 
                vax_pre_registrations (patient_id, patient_questionnaire_id, group_code)
            VALUES (%s, %s, %s)
        """
        vals = (patient_id, patient_questionnaire_id, group_code)
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


def create_vax_yes_patient(first_name, last_name, phone, email, dob, group_code):
    import uuid
    sql = """INSERT INTO patients (first_name, last_name, phone_number, email, dob, vax_yes_group_code, phone_number_verified, token) 
    values (%s, %s, %s, %s, %s, %s, %s, %s)"""
    vals = (first_name, last_name, phone, email,
            dob, group_code, 1, str(uuid.uuid4()))
    return exec_insert(sql, vals)


def create_cert(patient_id, vax_date, vax_type, lot, active=True):
    sql = """INSERT INTO ggv_certificates (patient_id, check_in_dt, service_code, lot_no, verification_level, active) 
       values (%s, %s, %s, %s, %s, %s)"""
    vals = (patient_id, vax_date, vax_type, lot, 1, active)
    return exec_insert(sql, vals)


def delete_cert(patient_id):
    print(patient_id)
    sqld = """DELETE FROM ggv_certificates where patient_id = %s and id <> 0"""
    deleted = exec_delete(sqld, (patient_id,))
    print(deleted)
    return deleted


# Define the escape character mappings here
escape_character_map = {
    "'": "\\'"
}


def remove_escape_sequences(characters):
    # if string
    if isinstance(characters, str):
        return characters.translate(str.maketrans(escape_character_map))
    return characters


def get_existing_patients(phone_number="", first_name="", last_name="", dob="", token=""):

    sanitized_first_name = remove_escape_sequences(first_name)
    sanitized_last_name = remove_escape_sequences(last_name)

    where_statement = "phone_number_verified = 1 AND token not like 'NOVERIFY%'"
    if phone_number != "":
        where_statement = "{} AND phone_number = '{}'".format(
            where_statement, phone_number)
    if first_name != "":
        where_statement = "{} AND first_name = '{}'".format(
            where_statement, sanitized_first_name)
    if last_name != "":
        where_statement = "{} AND last_name = '{}'".format(
            where_statement, sanitized_last_name)
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


def is_empty_field(field):
    return 0 if field != "" else 1


def get_existing_patient(phone_number="", first_name="", last_name="", dob="", token=""):

    query_phone_number = is_empty_field(phone_number)
    query_first_name = is_empty_field(first_name)
    query_last_name = is_empty_field(last_name)
    query_dob = is_empty_field(dob)
    query_token = is_empty_field(token)

    try:
        sql = """SELECT 
                        *
                    FROM
                        patients
                    WHERE
                        phone_number_verified = 1 AND token not like 'NOVERIFY%'
                    AND
                        (phone_number=%s or 1=%s)
                    AND
                        (first_name=%s or 1=%s)
                    AND
                        (last_name=%s or 1=%s)
                    AND
                        (dob=%s or 1=%s)
                    AND
                        (token=%s or 1=%s)
            """

        vals = (phone_number, query_phone_number, first_name, query_first_name,
                last_name, query_last_name, dob, query_dob, token, query_token)
        return replica_read_row(sql, vals)

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
    u_token, token_type = get_user_token_from_jwt(token)
    if token_type == 'multi':
        return None
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


def lock_slot(token, patient_id):
    try:
        u_token, token_type = get_user_token_from_jwt(token)
        if u_token is None:
            return None
        sql = """INSERT INTO
                        used_tokens
                    (token, patient_id)
                    VALUES (%s, %s)"""
        vals = (u_token, patient_id,)
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
        vals = (patient_id,)
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

        # When checking Table for duplicates, Null is the expected result
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


def get_patient_upfront_payment(service_codes: List[str], currency: str):
    try:
        sql = """
            SELECT 
                t2.selfpay_amount,
                t1.service_code,
                t1.service_name,
                t2.currency
            FROM
                services_catalog as t1
            JOIN
                services_payments as t2
            ON
                t1.id=t2.service_catalog_id
            WHERE
                t1.service_code in (%s)
                AND
                t2.currency=%s        
        """

        comma_separated_service_code = ".".join(service_codes)

        vals = (comma_separated_service_code, currency)
        rows = replica_read_rows(sql, vals)

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


def get_verification_level_from_patient_id(id, dob):
    try:
        sql = """SELECT 
                        gc.id,
                        gc.verification_level,
                        gc.service_code
                    FROM
                        ggv_certificates gc
                        JOIN patients p
                        ON p.id = gc.patient_id
                    WHERE 
                        gc.patient_id = %s AND date(p.dob) = %s AND rejected = 0;"""
        vals = (id, dob,)
        return read_rows(sql, vals)
    except Exception as err:
        log_generic(
            type=ERROR,
            id=id,
            function=whoami(),
            error=err
        )
        return None


def save_apple_wallet_updates(patient_id, device_id, pass_type, serial_no, pushToken):
    try:
        sql = """INSERT INTO apple_passes (patient_id, device_id, pass_type, serial_no, push_token, update_dt)
                    VALUES(%s, %s, %s, %s, %s, NOW()) ON DUPLICATE KEY UPDATE 
                    patient_id = VALUES(patient_id),
                    device_id = VALUES(device_id),
                    pass_type = VALUES(pass_type),
                    serial_no = VALUES(serial_no),
                    push_token = VALUES(push_token),
                    update_dt = VALUES(update_dt)
                    """
        vals = (patient_id, device_id, pass_type, serial_no, pushToken)
        return exec_insert(sql, vals)
    except Exception as err:
        log_generic(
            type=ERROR,
            id=id,
            function=whoami(),
            error=err
        )
        return None


def get_serial_no(devide_id):
    sql = """SELECT serial_no FROM apple_passes where device_id = %s"""
    vals = (devide_id,)
    return replica_read_row(sql, vals)


def update_group_code_for_existing_patient(req):
    sql = """ UPDATE patients
                  SET
                      vax_yes_group_code=%s,
                      update_dt=now()
                  WHERE
                    first_name = %s
                     AND
                    last_name = %s
                    AND
                    dob = %s
                    AND
                    phone_number = %s
                    AND
                    result_token = %s
                    AND
                    token_expire > NOW()
            """
    vals = (req.group_code, req.first_name,
            req.last_name, req.dob, req.phone_number, req.token)
    exec_update(sql, vals)


def get_existing_vax_certificates(phone_number):
    try:
        sql = """ SELECT  
                    p.id,
                    c.id
                   FROM
                        patients p 
                    INNER JOIN 
                        ggv_certificates c 
                    ON p.id = c.patient_id
                    WHERE
                        p.phone_number = %s
                    """
        vals = (phone_number,)
        return replica_read_rows(sql, vals)
    except Exception as err:
        log_generic(
            type=ERROR,
            id=id,
            function=whoami(),
            error=err
        )
        return []


def get_active_certificates(patient_id):
    try:
        sql = """ SELECT  
                    c.id
                   FROM
                      ggv_certificates c 
                    WHERE
                        c.patient_id = %s
                        AND
                        c.active = 1
                    """
        vals = (patient_id,)
        return replica_read_rows(sql, vals)
    except Exception as err:
        log_generic(
            type=ERROR,
            id=id,
            function=whoami(),
            error=err
        )
        return []


def update_certificates_to_active(payment_id):
    try:
        # Get the patient Id from session id
        sql_payment_table = """
            SELECT gp.patient_id
            FROM ggv_payments gp 
            JOIN ggv_certificates gc 
            ON gp.patient_id = gc.patient_id 
            WHERE gp.payment_id=%s
        """
        values_payment_table = (payment_id,)

        payment_info = read_row(sql_payment_table, values_payment_table)

        # No certificates are available to update
        if not payment_info:
            return None

        patient_id = payment_info['patient_id']

        sql = """ UPDATE ggv_certificates
                  SET
                      active=1,
                      update_dt=now()
                  WHERE
                    patient_id = %s
                     AND
                    active = 0
            """
        vals = (patient_id,)
        exec_update(sql, vals)
        # Return the patient id
        return patient_id
    except Exception as err:
        log_generic(
            type=ERROR,
            id=id,
            function=whoami(),
            error=err
        )
        return None


def save_vax_yes_payment_info(patient_id, payment_id, status):
    try:
        sql = """INSERT INTO ggv_payments (patient_id, payment_id, status)
                    VALUES(%s, %s, %s)
                    """
        vals = (patient_id, payment_id, status)
        return exec_insert(sql, vals)
    except Exception as err:
        log_generic(
            type=ERROR,
            id=id,
            function=whoami(),
            error=err
        )
        return None


def update_vax_yes_payment_status(status, payment_id):
    try:
        sql = """UPDATE ggv_payments
                 SET
                        status=%s,
                        update_dt=now()
                  WHERE
                     payment_id=%s
                  """
        vals = (status, payment_id)
        return exec_update(sql, vals)
    except Exception as err:
        log_generic(
            type=ERROR,
            vals=vals,
            function=whoami(),
            error=err
        )
        return None


def get_patient_by_id(patient_id):
    try:
        sql = """
            SELECT 
               *
            FROM 
                patients 
            WHERE 
                id=%s 
            LIMIT 1
        """
        vals = (patient_id,)
        row = read_row(sql, vals)

        log_generic(
            type=INFO,
            patient_id=patient_id,
            row=row,
            function=whoami()
        )

        # Return whole patient object
        return row
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
