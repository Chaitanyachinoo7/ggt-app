from ggt.lib.utils import (
    log_generic
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

def create_pending_signup_record(phone_number, otp, token=None, ip=None, device_data=None, status='pending'):
    try:
        sql = "INSERT INTO signups (phone_number, otp, ip, device_data, status, token) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (phone_number, otp, ip, device_data, status, token)
        return exec_insert(sql, val)

    except Exception as err:
        log_generic(type="error", phone_number=phone_number, otp=otp, token=token, ip=ip, device_data=device_data, status=status, function='__insert_record_signups', error=err)
        return None



def get_signup_record(id):
    try:
        sql = "SELECT * FROM signups WHERE id=%s"
        val = (id,)
        return read_row(sql, val)

    except Exception as err:
        log_generic(type="error", id=id, function='__read_record_signups_by_id', error=err)
        return None



def get_signup_record_by_phone_otp(phone_number, otp):
    try:
        sql = "SELECT token FROM signups WHERE phone_number=%s AND otp=%s"
        val = (phone_number, otp)
        row = read_row(sql, val)
        return row

    except Exception as err:
        log_generic(type="error", phone_number=phone_number, otp=otp, function='__read_record_signups', error=err)
        return None



def get_signup_record_by_token(token):
    try:
        sql = "SELECT * FROM signups WHERE token=%s"
        val = (token,)
        return read_row(sql, val)

    except Exception as err:
        log_generic(type="error", token=token, function='__read_record_signups_by_token', error=err)
        return None



def update_signup_record(id):
    try:
        sql = "UPDATE signups SET status='verified', modified_dt=NOW() WHERE (id=%s)"
        val = (id,)
        return exec_update(sql, val)

    except Exception as err:
        log_generic(type="error", id=id, function='__update_record_signups', error=err)
        return None


########################################################################################################
# [Protected] functions
########################################################################################################


