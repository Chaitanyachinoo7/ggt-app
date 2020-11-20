import os
import glob
import csv
import datetime
import paramiko
import base64
import random
from PIL import Image

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id,
    whoami
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    read_row,
    read_rows
)

from ggt.lib.storage import (
    file_exists_in_insurance_cards,
    upload_insurance_card_from_base64_string
)

import ggt.lib.constants as c

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

session_id = generate_session_id()


def task_process_misc():
    print('\n\n************************************************\n\n')
    log_generic(
        type=INFO,
        function=whoami(),
        task_session_id=session_id,
        info='Begin Processing Misc Task')

    # upload_insurance_images_to_gcp()
    sync_appointments_with_schedule_slots()

    log_generic(
        type=INFO,
        function=whoami(),
        task_session_id=session_id,
        info='End Processing outbound Lab Reports')
    print('\n\n************************************************\n\n')


def sync_appointments_with_schedule_slots():
    sql = """
        SELECT 
            id, scheduled_dt, location_id
        FROM
            appointments
        WHERE
            scheduled_dt > DATE(NOW())
            AND scheduled_dt < '2020-11-20'
                AND id NOT IN (
                    SELECT 
                        appointment_id
                    FROM
                        schedules
                    WHERE
                        appointment_id IS NOT NULL
                )
    """
    rows = read_rows(sql)
    print('Appointments loaded. Count: {}'.format(len(rows)))

    for row in rows:
        try:
            sql = """
                UPDATE schedules 
                SET 
                    status = 'booked',
                    appointment_id = %s
                WHERE
                    start_dt = %s
                    AND status = 'available' 
                    AND location_id = %s
                LIMIT 1
            """
            vals = (row['id'], row['scheduled_dt'], row['location_id'])
            #if exec_update(sql, vals):
            #    print(row['id'], row['scheduled_dt'])
            
            print("""UPDATE schedules SET status = 'booked', appointment_id = {} WHERE start_dt = '{}' AND location_id = {} AND status = 'available' LIMIT 1""".format(row['id'], row['scheduled_dt'], row['location_id']))

        except Exception as err:
            log_generic(
                type=c.ERROR,
                function=whoami(),
                error=err
            )


def upload_insurance_images_to_gcp():
    limit = 100000
    increment = 1000
    start = random.randint(0, 100000)
    start = 0
    print('starting at: ', start)
    try:
        for i in range(start, limit, increment):
            sql = """
            SELECT 
                q.id, a.id as appointment_id, q.patient_id, insurance_photo
            FROM
                patient_questionnaires q
                    JOIN
                appointments a ON (a.patient_id = q.patient_id)
            LIMIT {},{}
            """.format(i, increment)
            rows = read_rows(sql)

            for row in rows:
                try:
                    qid = row['id']
                    insurance_photo = row['insurance_photo']
                    appointment_id = row['appointment_id']

                    if insurance_photo is None or len(insurance_photo) < 250:
                        pass
                    else:
                        if "," in insurance_photo:
                            base64string = insurance_photo.split(",")[1]

                        dest_file_name = '{}.png'.format(appointment_id)
                        upload_insurance_card_from_base64_string(
                            base64string, 'image/png', dest_file_name)

                        print('uploaded image: {}'.format(dest_file_name))
                        remove_image_from_questionnnaires_table(qid)

                except Exception as err:
                    print(err)

    except Exception as err:
        print(err)


def remove_image_from_questionnnaires_table(id):
    try:
        sql = """
        UPDATE patient_questionnaires 
        SET 
            insurance_photo = 1
        WHERE
            id = %s
        """
        val = (id,)
        result = exec_update(sql, val)
        pass

    except Exception as err:
        print(err)
