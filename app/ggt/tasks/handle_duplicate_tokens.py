import csv
import pathlib
from datetime import datetime
from ggt.lib.adapters.mysql_adapter import exec_batch_execute, replica_read_row, replica_read_rows, exec_update
from ggt.lib.utils import generate_token


def handle_duplicate_tokens_old():
    """Get all duplicate tokens"""
    limit = 2
    offset = 0
    sql_1 = """SELECT 
                    id
                FROM
                    patients
                WHERE
                    token IN (SELECT 
                            token
                        FROM
                            (SELECT 
                                COUNT(*) AS x, token
                            FROM
                                ggt_prod.patient_questionnaires
                            GROUP BY token
                            HAVING x > 1) x)
                LIMIT {} OFFSET {};
                """

    while offset < 50000:
        rows = replica_read_rows(sql_1.format(limit, offset))
        offset = offset + limit
        for row in rows:
            t_1 = datetime.now()
            patient_id = row['id']
            token = generate_token()

            s_1 = update_token_patient(patient_id, token)
            s_2 = update_token_ques(patient_id, token)

            t_2 = datetime.now()
            time_taken = (t_2 - t_1).seconds
            print("patient - {}, token - {} : s1 - {} s2 - {} : time - {} seconds".format(patient_id, token, s_1, s_2, time_taken))


def update_token_patient(patient_id, token):
    sql = """UPDATE patients
		     SET token = %s
		     WHERE id = %s;"""
    vals = (token, patient_id)
    return exec_update(sql, vals)

def update_token_ques(patient_id, token):
    sql = """UPDATE patient_questionnaires
    		 SET token = %s
    		 WHERE patient_id = %s;"""
    vals = (token, patient_id)
    return exec_update(sql, vals)


#handle_duplicate_tokens()


"""
In PROD we have 26522 records. One record takes around 7 seconds in local machine, it is just above 2 days
"""



def handle_duplicate_tokens():
    sql = """
        SELECT 
            result_token, COUNT(result_token) AS cnt
        FROM
            patients
        GROUP BY result_token
        HAVING COUNT(*) > 1
    """
    rows = replica_read_rows(sql)
    
    for row in rows:
        try:
            t_1 = datetime.now()
            sql2 = """
                SELECT 
                    id
                FROM
                    patients
                WHERE
                    result_token = %s
                LIMIT 1
            """
            vals2 = (row['result_token'],)
            row2 = replica_read_row(sql2, vals2)

            patient_id = row2['id']
            token = generate_token()

            s_1 = update_token_patient(patient_id, token)
            #s_2 = update_token_ques(patient_id, token)

            t_2 = datetime.now()
            time_taken = (t_2 - t_1).seconds
            print("patient - {}, token - {} : s1 - {}: time - {} seconds".format(patient_id, token, s_1, time_taken))
        
        except Exception:
            pass