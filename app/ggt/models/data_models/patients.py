from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami, generate_token
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
    GgtPatient
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
                    token_expire
                )
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, DATE_ADD(NOW(), interval 10 minute))
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
            patient.token
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


def get_existing_patients(phone_number="", first_name="", last_name="", dob=""):

    where_statement = "phone_number_verified = 1"
    if phone_number != "":
        where_statement = "{} AND phone_number = '{}'".format(where_statement, phone_number)
    if first_name != "":
        where_statement = "{} AND first_name = '{}'".format(where_statement, first_name)
    if last_name != "":
        where_statement = "{} AND last_name = '{}'".format(where_statement, last_name)
    if dob != "":
        where_statement = "{} AND dob = '{}'".format(where_statement, dob)
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
            vals=vals,
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


def unlock_patient_info_patients(phone_number):
    try:
        result_token = generate_token()
        sql = """UPDATE patients 
                    SET 
                        result_token = %s,
                        token_expire = DATE_ADD(NOW(), interval 10 minute)
                    WHERE
                        phone_number = %s"""
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

########################################################################################################
# [Protected] functions
########################################################################################################
