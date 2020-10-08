from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
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
        vals = (phone_number, otp, ip, device_data, status, token)
        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(type=ERROR, phone_number=phone_number, otp=otp, token=token, ip=ip,
                    device_data=device_data, status=status, function=whoami(), error=err)
        return None


def get_signup_record(id):
    try:
        sql = "SELECT * FROM signups WHERE id=%s"
        vals = (id,)
        return read_row(sql, vals)

    except Exception as err:
        log_generic(type=ERROR, id=id, function=whoami(), error=err)
        return None


def get_signup_record_by_phone_otp(phone_number, otp):
    try:
        sql = "SELECT token FROM signups WHERE phone_number=%s AND otp=%s"
        vals = (phone_number, otp)
        row = read_row(sql, vals)
        return row

    except Exception as err:
        log_generic(type=ERROR, phone_number=phone_number,
                    otp=otp, function=whoami(), error=err)
        return None


def get_signup_record_by_token(token):
    try:
        sql = "SELECT * FROM signups WHERE token=%s"
        vals = (token,)
        return read_row(sql, vals)

    except Exception as err:
        log_generic(type=ERROR, token=token, function=whoami(), error=err)
        return None


def update_signup_record(id):
    try:
        sql = "UPDATE signups SET status='verified', modified_dt=NOW() WHERE (id=%s)"
        vals = (id,)
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(type=ERROR, id=id, function=whoami(), error=err)
        return None


def get_ui_screen_flow_seq(group_code):
    try:
        sql = "SELECT * FROM groups WHERE group_code=%s LIMIT 1"
        vals = (group_code,)
        return read_row(sql, vals)

    except Exception as err:
        log_generic(type=ERROR, group_code=group_code,
                    function=whoami(), error=err)
        return None

########################################################################################################
# [Protected] functions
########################################################################################################
