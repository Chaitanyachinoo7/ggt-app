from ggt.lib.utils import (
    log_generic,
    get_config_val
)

from ggt.models.data_models.appointments import (
    get_appointment,
    update_appointment_with_checkin,
    update_appointment_with_test_start,
    update_appointment_with_test_completed
)

'''
,
    get_monthy_calendar,
    positive_result_followup,
    update_positive_result_followup,
    get_user_role,
    get_test_results
'''

from ggt.lib.sys_log import (write_syslog)
import datetime
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
        if appointment['status']=='pending':
            return False
        else:
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


def bp_appointment_update(appointment_id, action, workstation_id):
    try:
        appointment = get_appointment(appointment_id)

        if action == 'checkin' or action == 'check_in':
            update_appointment_with_checkin(appointment_id)
        elif action == 'start_test':
            __appointment_begin_test(appointment_id, workstation_id)
        elif action == 'end_test':
            update_appointment_with_test_completed(appointment_id)
        elif action == 'reprint':
            __appointment_begin_test(appointment_id, workstation_id)

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

'''
def bp_get_monthly_calendar(date, location_id):
    try:
        print(date, location_id)
        date_time_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        from_date = date_time_obj.date().replace(day=1)
        to_date = date_time_obj.date().replace(day=31)
        results = get_monthy_calendar(from_date, to_date, location_id)
        # print(results)
        response = []
        for record in results:
            # print(record)
            appointment = {}
            appointment['title'] = record['last_name'] + \
                ", " + record['first_name']
            appointment['start'] = record['scheduled_dt']
            appointment['end'] = record['scheduled_dt'] + \
                datetime.timedelta(minutes=30)
            appointment['allDay'] = False
            appointment['backgroundColor'] = "#3c8dbc"
            response.append(appointment)
        return response
    except Exception as err:
        log_generic(
            type="error",
            date=date,
            location_id=location_id,
            function='bp_get_monthly_calendar',
            error=err
        )


def bp_provider_positive_result_followup():
    try:
        results = positive_result_followup()
        update_positive_result_followup(
            results['test_id'], datetime.datetime.now())
        return results
    except Exception as err:
        log_generic(
            type="error",
            location_id="",
            function='bp_provider_positive_result_followup',
            error=err
        )


'''
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
    return dob.strftime("%m/%d/%Y")


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

        queue_url = "{}-{}".format(get_config_val('aws.sqs_print_queue_base_url'), queue_id)

        write_syslog("print", "info", appointment_id)

        # TODO FIX all this
        payload = {
            "barcode_text": "{}".format(appointment_id),
            "name_text": patient_name,
            "dob_text": appointment['dob'].strftime("%m/%d/%Y"),
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
                    function='__appointment_begin_test', error=err)
        write_syslog("print", "error", appointment_id)
        return False
