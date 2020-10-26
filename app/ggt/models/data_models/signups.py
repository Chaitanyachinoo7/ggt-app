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

from ggt.models.data_models.data_types import (
    GgtThirdPartyGroup
)
########################################################################################################
# [Public] functions
########################################################################################################


def create_pending_signup_record(phone_number, otp, token=None, ip=None, device_data=None, status='pending'):
    try:
        sql = """
        INSERT INTO signups 
            (
                phone_number, 
                otp, 
                ip, 
                device_data, 
                status, 
                token
            ) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        vals = (
            phone_number, 
            otp, 
            ip, 
            device_data, 
            status, 
            token
        )
        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR, 
            phone_number=phone_number, 
            otp=otp, 
            token=token, 
            ip=ip,
            device_data=device_data, 
            status=status, 
            function=whoami(), 
            error=err
        )
        return None


def get_signup_record(id):
    try:
        sql = """
        SELECT * 
        FROM 
            signups 
        WHERE 
            id = %s
        """
        vals = (id,)
        return read_row(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR, 
            id=id, 
            function=whoami(), 
            error=err
        )
        return None


def get_signup_record_by_phone_otp(phone_number, otp):
    try:
        sql = """
        SELECT token 
        FROM 
            signups 
        WHERE 
            phone_number = %s 
            AND otp = %s
        """
        vals = (phone_number, otp)
        row = read_row(sql, vals)
        if row:
            return row['token']
        return None

    except Exception as err:
        log_generic(
            type=ERROR, 
            phone_number=phone_number,
            otp=otp, 
            function=whoami(), 
            error=err
        )
        return None


def get_signup_record_by_token(token):
    try:
        sql = """
        SELECT * 
        FROM 
            signups 
        WHERE 
            token = %s
        """
        vals = (token,)
        return read_row(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR, 
            token=token, 
            function=whoami(), 
            error=err
        )
        return None


def update_signup_record(id):
    try:
        sql = """
        UPDATE signups 
        SET 
            status='verified', 
            modified_dt = NOW() 
        WHERE 
            id = %s
        """
        vals = (id,)
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR, 
            id=id, 
            function=whoami(), 
            error=err
        )
        return None


def get_group_info(group_code: str) -> GgtThirdPartyGroup:
    group_info: GgtThirdPartyGroup = None
    try:
        sql = """
        SELECT * 
        FROM 
            groups 
        WHERE 
            group_code = %s 
        LIMIT 1
        """
        vals = (group_code,)
        group_info = __map_row_to_group(
            read_row(sql, vals)
        )

    except Exception as err:
        log_generic(
            type=ERROR, 
            group_code=group_code,
            function=whoami(), 
            error=err
        )

    return group_info

########################################################################################################
# [Protected] functions
########################################################################################################

def __map_row_to_group(row) -> GgtThirdPartyGroup:
    g: GgtThirdPartyGroup = GgtThirdPartyGroup()
    try:
        g.account_name = row['account']
        g.group_code = row['group_code']
        g.is_refferal_code = row['is_referral_code']
        g.consent_req = row['consent_req']
        g.collect_insurance = row['collect_insurance']
        g.insurance_req = row['insurance_req']
        g.allow_insurance_skip = row['allow_insurance_skip']
        g.upfront_payment_req = row['upfront_payment_req']
        g.display_group_consent = row['display_group_consent']
        g.consent_party_name = row['consent_party_name']
        g.consent_url = row['consent_url']
        g.logo_1 = row['logo_1']
        g.logo_2 = row['logo_2']
        if row['required_screens']:
            g.required_screens = row['required_screens'].split(',')
        if row['screen_seq']:
            g.screen_seq = row['screen_seq'].split(',')

    except Exception as err:
        log_generic(
            type=ERROR, 
            row=row,
            function=whoami(), 
            error=err
        )

    return g
    