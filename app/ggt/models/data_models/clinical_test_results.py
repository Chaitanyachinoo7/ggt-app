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

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    replica_read_row,
    replica_read_rows
)


########################################################################################################
# [Public] functions
########################################################################################################
def get_test_result(id):
    try:
        sql = """
                SELECT * 
                FROM detailed_test_results 
                WHERE id = %s
                LIMIT 1
            """
        vals = (id,)
        return replica_read_row(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR, 
            id=id, 
            function=whoami(), 
            error=err
        )
        return False


def get_test_result_by_token(token, test_id=""):
    try:
        sql = """
                SELECT * 
                FROM detailed_test_results 
                WHERE token = %s
                AND test_result IS NOT NULL
                AND ("" = %s OR test_id = %s)
                ORDER by test_id DESC
                LIMIT 1
            """
        vals = (token, test_id, test_id,)
        return replica_read_row(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR, 
            token=token,
            function=whoami(), 
            error=err
        )
        return False


def get_test_details(test_id):
    try:
        sql = """
                SELECT * 
                FROM detailed_test_results 
                WHERE test_id = %s
                ORDER by test_id DESC
                LIMIT 1
            """
        vals = (test_id,)
        return replica_read_row(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR, 
            test_id=test_id,
            function=whoami(), 
            error=err
        )
        return False


def search_details_by_name_and_dob(last_name, dob):
    try:
        sql = """
                SELECT 
                    t.test_id,
                    t.first_name,
                    t.last_name,
                    t.dob,
                    t.phone_number,
                    t.email,
                    t.addr1 as p_addr1,
                    t.city as p_city,
                    t.st as p_st,
                    t.zip as p_zip,
                    t.sample_collection_start_dt,
                    t.token,
                    g.group_code,
                    g.account,
                    l.addr1,
                    l.city,
                    l.st,
                    l.zip,
                    (CASE
                        WHEN (test_result IS NULL) THEN 'Pending'
                        ELSE 'Available'
                    END) AS result
                FROM
                    detailed_test_results t
                    LEFT JOIN locations l ON t.sample_collection_location_id = l.id
                    INNER JOIN group_codes_to_locations_mapping m ON t.sample_collection_location_id = m.location_id
                    INNER JOIN groups g ON g.id = m.group_id
                WHERE
                    last_name LIKE %s
                        AND dob = %s
                ORDER BY t.test_id DESC
            """
        vals = ('%'+last_name+'%', dob)
        return replica_read_rows(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            last_name=last_name,
            dob=dob,
            function=whoami(),
            error=err
        )
        return False


def get_all_test_results():
    try:
        sql = """
                SELECT 
                    pat.id as patient_id,
                    ts.id as test_id,
                    pat.dob,
                    pat.first_name, 
                    pat.last_name, 
                    pat.phone_number, 
                    pat.email,
                    pat.gender,
                    pat.addr1,
                    pat.city,
                    pat.st,
                    pat.zip,
                    ts.group_code,
                    ts.test_result,
                    ts.status
                FROM
                    patients pat
                INNER JOIN test_samples ts
                    ON pat.id = ts.patient_id
            """
        return replica_read_rows(sql, )

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )

########################################################################################################
# [Protected] functions
########################################################################################################
