from ggt.lib.utils import (
    log_generic,
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows
)

########################################################################################################
# [Public] functions
########################################################################################################
def create_patient_record(**kwargs):
    try:
        token = kwargs.get('token', '')
        phone_number = kwargs.get('phone_number', '')
        phone_number_verified = kwargs.get('phone_number_verified', '')
        email = kwargs.get('email', '')

        first_name = kwargs.get('first_name', '')
        middle_name = kwargs.get('middle_name', '')
        last_name = kwargs.get('last_name', '')
        gender = kwargs.get('gender', '')
        
        dob = kwargs.get('dob', '')
        height_ft = kwargs.get('height_ft', '')
        weight_lb = kwargs.get('weight_lb', '')

        ethnicity = kwargs.get('ethnicity', '')
        race = kwargs.get('race', '')

        addr1 = kwargs.get('addr1', '')
        city = kwargs.get('city', '')
        zip = kwargs.get('zip', '')
        st = kwargs.get('st', '')
 
        sql = "INSERT INTO patients (first_name, middle_name, last_name, addr1, city, st, zip, \
                gender, height_ft, weight_lb, ethnicity, race,  dob, phone_number, phone_number_verified, email, token) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        val = (first_name, middle_name, last_name, addr1, city, st, zip,
               gender, height_ft, weight_lb, ethnicity, race,  dob, phone_number, phone_number_verified, email, token)

        return exec_insert(sql, val)

    except Exception as err:
        log_generic(type="error", data=data, locals=locals(),
                    function='create_patient_record', error=err)
        return None


def get_patient(patient_id):
    try:
        sql = "SELECT id, first_name, middle_name, last_name, dob, token FROM patients WHERE id=%s LIMIT 1"
        val = (id,)
        row = read_row(sql, val)
        log_generic(type="info", id=id, row=row,
                    function='__read_record_patients_by_id')
        return (row['id'], row['first_name'], row['middle_name'], row['last_name'], row['dob'], row['token'])

    except Exception as err:
        log_generic(type="error", id=id,
                    function='get_patient_by_id', error=err)
        return None


def get_patient_by_token(token):
    try:
        sql = "SELECT id, first_name, middle_name, last_name, dob, token FROM patients WHERE token=%s LIMIT 1"
        val = (token,)
        row = read_row(sql, val)
        log_generic(
            type="info", 
            token=token, 
            function='get_patient_by_token')
        return (row['id'], row['first_name'], row['middle_name'], row['last_name'], row['dob'], row['token'])

    except Exception as err:
        log_generic(
            type="error", 
            id=id,
            function='get_patient_by_token', 
            error=err)
        return None

########################################################################################################
# [Protected] functions
########################################################################################################
