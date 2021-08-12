import csv
import pathlib
from datetime import datetime
# ORGANIZATION_ID = 1
# SEASON_ID = 1
# PATH = pathlib.Path(__file__).parent.absolute()

from ggt.lib.adapters.mysql_adapter import exec_batch_execute, replica_read_rows, exec_update
from ggt.models.process_models.bp_patient_experience import bp_finalize_payment
from ggt.models.process_models.bp_payment import bp_get_checkout_session


def update_stripe_payments():
    selected_ids = []
    notification_queue = []
    print("****************************** START - PAYMENT ******************************")
    appointments = get_scheduled_paid_appointments()
    for a in appointments:
        try:
            appointment_id = a['id']
            payment_session = a['payment_session']
            wp_receipt_token = a['wp_receipt_token']
            res = bp_get_checkout_session(payment_session)

            if (res and 'payment_status' in res.keys()) and res['payment_status'] == 'paid':
                temp = {
                    'appointment_id': appointment_id,
                    'wp_receipt_token': wp_receipt_token
                }
                selected_ids.append(appointment_id)
                notification_queue.append(temp)

        except Exception as err:
            print('PAYMENT PROCESS ERROR')
            print(err)

    updated = update_appointments_stripe(selected_ids)
    print("*. IDs updated {}".format(updated))
    notify_patients(notification_queue)
    print("******************************* END - PAYMENT *******************************")


def get_scheduled_paid_appointments():
    sql = """
            SELECT * FROM
                    appointments
                    WHERE
                    status = %s AND payment_session IS NOT NULL LIMIT 100"""

    values = ('pending', )
    return replica_read_rows(sql, values)


def update_appointments_stripe(id_list):
    if len(id_list) < 2:
        id_list.append(0)
    print("*. Selected IDs - {}".format(id_list))
    sql = """UPDATE appointments 
                    SET 
                        status = %s
                    WHERE id IN {}""".format(str(tuple(id_list)))
    values = ('scheduled',)
    return exec_update(sql, values)


def notify_patients(notification_queue):
    for a in notification_queue:
        appointment_id = a['appointment_id']
        wp_receipt_token = a['wp_receipt_token']
        print("*. Notifying {} - {}".format(appointment_id, wp_receipt_token))
        bp_finalize_payment(appointment_id, wp_receipt_token)
