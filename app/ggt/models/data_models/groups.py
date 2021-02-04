from ggt.lib.adapters.auth0_adapter import get_organization_id
from ggt.lib.adapters.auth0_config import META_KEY, ORGANIZATION_KEY
from ggt.lib.db import (
    read_rows,
    exec_insert, exec_update, replica_read_rows)
from ggt.lib.constants import (
    ERROR
)
from ggt.lib.utils import (
    log_generic,
    whoami
)


########################################################################################################
# [Public] functions
########################################################################################################
def get_all_groups(user):
    try:
        organization_id = get_organization_id(user)
        if organization_id is None:
            return None

        sql = """SELECT * FROM groups"""
        return replica_read_rows(sql)

        '''If groups are not shared Use this'''
        # sql = """SELECT * FROM groups
        #             WHERE org_id = %s"""
        # vals = (organization_id, )
        # return replica_read_rows(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def create_group(group):
    try:
        sql = """INSERT INTO groups
                (
                    account,
                    group_code,
                    is_referral_code,
                    consent_req,
                    collect_insurance,
                    insurance_req,
                    allow_insurance_skip,
                    upfront_payment_req,
                    screen_seq,
                    required_screens,
                    display_group_consent,
                    consent_party_name,
                    consent_url,
                    logo_1,
                    logo_2,
                    optional_screens
                )
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
        vals = (
            group.account,
            group.group_code,
            group.is_referral_code,
            group.consent_req,
            group.collect_insurance,
            group.insurance_req,
            group.allow_insurance_skip,
            group.upfront_payment_req,
            group.screen_seq,
            group.required_screens,
            group.display_group_consent,
            group.consent_party_name,
            group.consent_url,
            group.logo_1,
            group.logo_2,
            group.optional_screens
        )
        group_id = exec_insert(sql, vals)
        return group_id

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_group_by_id(id):
    try:
        sql = """SELECT * FROM groups WHERE id = %s"""
        vals = (id,)
        return read_rows(sql, vals)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def update_group(group):
    try:
        sql = """
               UPDATE groups SET
                    account = %s,
                    group_code = %s,
                    is_referral_code = %s,
                    consent_req = %s,
                    collect_insurance = %s,
                    insurance_req = %s,
                    allow_insurance_skip = %s,
                    upfront_payment_req = %s,
                    screen_seq = %s,
                    required_screens = %s,
                    display_group_consent = %s,
                    consent_party_name = %s,
                    consent_url = %s,
                    logo_1 = %s,
                    logo_2 = %s,
                    optional_screens = %s
               WHERE id =  %s
                        """
        vals = (
            group.account,
            group.group_code,
            group.is_referral_code,
            group.consent_req,
            group.collect_insurance,
            group.insurance_req,
            group.allow_insurance_skip,
            group.upfront_payment_req,
            group.screen_seq,
            group.required_screens,
            group.display_group_consent,
            group.consent_party_name,
            group.consent_url,
            group.logo_1,
            group.logo_2,
            group.optional_screens,
            group.id
        )
        updated = exec_update(sql, vals)
        return updated

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None