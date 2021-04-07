import csv
import pathlib
from datetime import datetime
# ORGANIZATION_ID = 1
# SEASON_ID = 1
# PATH = pathlib.Path(__file__).parent.absolute()

from ggt.lib.adapters.mysql_adapter import exec_batch_execute, replica_read_rows, exec_update
from ggt.lib.utils import get_config_val

lab_report_bucket = get_config_val('lab_integrations.labreport_bucket')


def generate_antigen_results_pdf():
    rows = get_all_appointment_information()
    processed_appointment_ids = generate_results_pdf(rows)
    update_test_samples(processed_appointment_ids)


def get_all_appointment_information():
    sql = """SELECT 
                    p.first_name,
                    p.last_name,
                    p.dob,
                    p.gender,
                    ts.test_result,
                    ts.sample_collection_end_dt,
                    ts.lab_electronic_submission_dt AS 'report_gen_dt',
                    ts.appointment_id,
                    ts.id
                FROM
                    test_samples ts
                        JOIN
                    appointment_services aps ON ts.appointment_id = aps.appointment_id
                        JOIN
                    services_catalog sc ON sc.id = aps.service_id
                        JOIN
                    patients p ON ts.patient_id = p.id
                WHERE
                    sc.service_code LIKE '%ANTIGEN%'
                        AND ts.status = 'with_lab';"""

    return replica_read_rows(sql)


def generate_results_pdf(rows):
    success_appointment_ids = []

    for row in rows:
        '''
            1. Generate the result PDF
            2. Upload it to lab_report_bucket (defined above)
            3. if success add appointment ID to success_appointment_ids
        '''
    return success_appointment_ids


def update_test_samples(processed_appointment_ids=[]):
    if len(processed_appointment_ids) < 2:
        processed_appointment_ids.append(0)

    sql = """UPDATE test_samples 
                    SET 
                        lab_result_receive_dt = NOW(),
                        status = 'lab_result_received'
                    WHERE id IN {}""".format(str(tuple(processed_appointment_ids)))
    return exec_update(sql)