from ggt.lib.utils import (
    log_generic
)

from ggt.models.data_models.appointments import (
    get_appointment,
    update_appointment_with_checkin,
    update_appointment_with_test_start,
    update_appointment_with_test_completed,
)

from ggt.lib.sys_log import (write_syslog)
'''
from ggt.models.data_models.test_results import (
    update_appointment_with_checkin,
    update_test_with_test_start,
    update_test_with_test_completed
)
'''
########################################################################################################
# [Public] functions
########################################################################################################


def bp_get_appointment_info(appointment_id):
    try:
        appointment = get_appointment(appointment_id)
        return {
            "appointment_id": appointment_id,
            "date": __formatted_date_text(appointment),
            "location": __formatted_location_text(appointment),
            "patient_dob": __formatted_patient_dob(appointment),
            "patient_name": __formatted_patient_name(appointment),
            "patient_address": __formatted_patient_address(appointment),
            "next_action": __next_action(appointment)
        }
    except Exception as err:
        log_generic(
            type="error",
            appointment_id=appointment_id,
            function='bp_get_appointment_info',
            error=err
        )
        return False


def bp_appointment_update(appointment_id, action):
    try:
        appointment = get_appointment(appointment_id)

        if action == 'checkin' or action == 'check_in':
            update_appointment_with_checkin(appointment_id)
        elif action == 'start_test':
            __appointment_begin_test(appointment_id)
        elif action == 'end_test':
            update_appointment_with_test_completed(appointment_id)
        elif action == 'reprint':
            # TODO: Handle reprint request
            pass

        return {
            'appointment_id': appointment_id,
            'next_action': __next_action(appointment),
        }
    except Exception as err:
        log_generic(
            type="error",
            appointment_id=appointment_id,
            function='bp_get_appointment_info',
            error=err
        )
    
    return False


########################################################################################################
# [Protected] functions
########################################################################################################
def __formatted_date_text(appointment):
    return appointment['scheduled_dt'].strftime("%a, %-d %b %Y @ %-I:%M %p")


def __formatted_location_text(appointment):
    # 6155 Sports Village Rd, Frisco, TX 75033
    return "{}, {} {}  {}".format(appointment['addr1'],
                                  appointment['city'],
                                  appointment['st'],
                                  appointment['zip'])


def __formatted_patient_address(appointment):
    return "{}, {} {}  {}".format(appointment['patient_addr1'],
                                  appointment['patient_city'],
                                  appointment['patient_st'],
                                  appointment['patient_zip'])


def __formatted_patient_name(appointment):
    return "{} {} {}".format(
        appointment['first_name'],
        appointment['middle_name'],
        appointment['last_name'])


def __formatted_patient_dob(appointment):
    dob = appointment['dob']
    if len(dob) == 8:
        return "{}/{}/{}".format(dob[0:2], dob[2:4], dob[4:8])
    else:
        return "{}/{}/19{}".format(dob[0:2], dob[2:4], dob[4:6])


def __next_action(appointment):
    switcher = {
        'scheduled': 'check_in',
        'checked_in': 'start_test',
        'test_in_progress': 'end_test'
    }
    return switcher.get(appointment['status'], "")
        





# TODO: Multilane printer setup
def __appointment_begin_test(appointment_id, queue_id=1):
    update1 = update_appointment_with_test_start(appointment_id)
    #update2 = begin_test(appointment_id, patient_id)

    # send label to printer
    import json
    import boto3

    try:
        appointment = get_appointment(appointment_id)
        date_text = appointment['scheduled_dt'].strftime(
            "%a, %-d %b %Y @ %-I:%M %p")
        patient_name = "{}, {} {}".format(appointment['last_name'],
                                          appointment['first_name'],
                                          appointment['middle_name'],
                                          )

        # TODO: Dynamic queue mamagement
        # have a group code
        if appointment['group_code'] != "":
            queue_id = 3

        if queue_id == 1:
            queue_url = 'https://sqs.us-east-1.amazonaws.com/343550539982/ggt-print-queue'
        elif queue_id == 2:
            queue_url = 'https://sqs.us-east-1.amazonaws.com/343550539982/ggt-print-queue-2'
        elif queue_id == 3:
            queue_url = 'https://sqs.us-east-1.amazonaws.com/343550539982/ggt-print-queue-3'

        write_syslog("print", "info", appointment_id)

        # TODO FIX all this
        payload = {
            "barcode_text": "{}".format(appointment_id),
            "name_text": patient_name,
            "dob_text": appointment['dob'],
            "timestamp_text": date_text
        }

        sqs = boto3.client(
            "sqs",
            aws_access_key_id='AKIAIWUMFU2SPDC7KBAQ',
            aws_secret_access_key='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',
            region_name='us-east-1'
        )
        response = sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=10,
            MessageBody=(json.dumps(payload))
        )
        print(response['MessageId'])
        # __log_generic(payload)
        #add_syslog_entry("print", "info", barcode_text)
        return True

    except Exception as err:
        log_generic(type="error", appointment_id=appointment_id,
                    function='appointment_begin_test', error=err)
        write_syslog("print", "error", appointment_id)
        return False


'''
def begin_test(appointment_id, patient_id, patient_questionnaire_id, group_code, location_id):
    __insert_record_test_samples(appointment_id, patient_id, patient_questionnaire_id, group_code, location_id)
    return True


def end_test(appointment_id):
    #update = __update_test_sample_with_end(appointment_id)
    return True
'''
