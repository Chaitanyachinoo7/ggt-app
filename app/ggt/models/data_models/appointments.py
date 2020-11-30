from datetime import datetime
from contextlib import suppress

import ggt.lib.constants as c

from ggt.lib.utils import (
    log_generic,
    whoami
)

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows
)

from ggt.models.data_models.data_types import (
    GgtAppointment,
    GgtBooking,
    GgtLocation,
    GgtPatient
)

########################################################################################################
# [Public] functions
########################################################################################################


async def create_appointment(appointment_req: GgtBooking):
    try:
        sql = """
        INSERT INTO appointments
        (
            scheduled_dt,
            location_id,
            patient_id,
            patient_questionnaire_id,
            group_code,
            total_cost,
            billed_amount
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        vals = (
            appointment_req.timeslot.start_dt,
            appointment_req.location_id,
            appointment_req.patient_id,
            appointment_req.patient_questionnaire_id,
            appointment_req.group_code,
            appointment_req.total_cost/100,  # cents --> decimal
            appointment_req.billed_amount/100  # cents --> decimal
        )
        appointment_id = await exec_insert(sql, vals)
        await __add_services_to_appointment(appointment_id, appointment_req)
        return await get_appointment(appointment_id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            appointment_req=appointment_req,
            error=err
        )

    return None


async def add_service_to_appointment(appointment_id: int, service_code: str) -> bool:
    try:
        sql = """
        INSERT INTO appointment_services
        (
            appointment_id,
            service_id,
            service_description,
            price,
            selfpay_amount,
            copay_amount,
            insurance_amount
        )
        SELECT 
            '{}' as appointment_id,
            id as service_id,
            service_name,
            price,
            selfpay_amount,
            copay_amount,
            insurance_amount
        FROM
            services_catalog
        WHERE
            service_code = %s
            
        """.format(appointment_id)
        vals = (service_code, )
        if exec_insert(sql, vals):
            return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            appointment_id=appointment_id,
            service_code=service_code,
            error=err
        )

    return False


async def get_appointment(appointment_id: int):
    try:
        sql = """
        SELECT 
            a.*,
            l.addr1 AS location_addr1,
            l.addr2 AS location_addr2,
            l.city AS location_city,
            l.st AS location_st,
            l.zip AS location_zip,
            l.lat,
            l.lng,
            p.dob AS patient_dob,
            p.first_name AS patient_first_name,
            p.middle_name AS patient_middle_name,
            p.last_name AS patient_last_name,
            p.addr1 AS patient_addr1,
            p.addr2 AS patient_addr2,
            p.city AS patient_city,
            p.st AS patient_st,
            p.zip AS patient_zip,
            p.phone_number AS patient_phone_number,
            p.email,
            p.gender,
            p.dob,
            GROUP_CONCAT(c.service_code) as service_codes,
            GROUP_CONCAT(s.service_description) as service_descriptions
        FROM
            appointments a
                JOIN
            patients p ON a.patient_id = p.id
                JOIN
            locations l ON a.location_id = l.id
                LEFT JOIN
            appointment_services s ON (s.appointment_id = a.id)
                LEFT JOIN
            services_catalog c ON (c.id = s.service_id)
        WHERE
                a.id = %s
        """

        vals = (appointment_id,)
        row = await read_row(sql, vals)

        if not row:
            raise ValueError('No Appointment info')

        return __map_row_to_appointment(row)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )

    return None


async def get_monthy_calendar(from_date: str, to_date: str, location_id: int):
    try:
        sql = """
            SELECT * 
            FROM 
                appointment_with_patient
            WHERE
                scheduled_dt between %s AND %s
                AND location_id = %s
            """

        vals = (from_date, to_date, location_id)
        return await read_rows(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            location_id=location_id,
            from_date=from_date,
            to_date=to_date,
            function=whoami(),
            error=err
        )

    return None


async def positive_result_followup():
    try:
        sql = """
            SELECT
                pos.patient_id,
                pos.test_id,
                pos.dob,
                pos.first_name,
                pos.last_name,
                pos.phone_number,
                pos.email,
                pat.gender,
                pat.addr1,
                patq.heart_disease,
                patq.diabetes,
                patq.respiratory_diseases,
                patq.autoimmune_disease,
                patq.other_chronic,
                patq.allergies,
                patq.prescription_use,
                patq.symptom_fever,
                patq.symptom_shortness_breath,
                patq.symptom_cough,
                patq.symptom_chest_pain,
                patq.symptom_lack_of_smell,
                patq.symptom_lack_of_smell,
                patq.symptom_other_breathing,
                patq.covid_contact
            FROM
                positive_result_followup_queue pos
            INNER JOIN patients pat
                ON pos.patient_id = pat.id
            INNER JOIN patient_questionnaires patq
                ON patq.patient_id = pat.id
            WHERE
                overall_status = %s LIMIT 1
        """

        vals = ("scheduled",)
        return await read_row(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )

    return None


async def update_appointment_with_receipt_token(appointment: GgtAppointment):
    try:
        sql = """
            UPDATE appointments
            SET
                wp_receipt_token = %s
            WHERE
                id = %s
        """
        vals = (appointment.wp_receipt_token, appointment.id)
        return await exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment=appointment,
            function=whoami(),
            error=err
        )

    return None
    

async def update_positive_result_followup(id: int, date_time: datetime):
    try:
        sql = """
            UPDATE positive_result_followup_queue
            SET
                overall_status = %s, update_dt = %s
            WHERE
                test_id = %s
            """

        vals = ("pending", date_time, id)
        return await exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            id=id,
            date_time=date_time,
            function=whoami(),
            error=err
        )

    return None


async def update_appointment_with_checkin(appointment_id: int):
    try:
        sql = """
            UPDATE appointments
            SET
                check_in_dt = NOW(),
                status = 'checked_in'
            WHERE
                id = %s
        """
        vals = (appointment_id,)
        return await exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )

    return None


async def update_appointment_with_test_start(appointment_id: int):
    try:
        sql = """
            UPDATE appointments
            SET
                test_start_dt = NOW(),
                status = 'test_in_progress'
            WHERE
                id = %s
        """
        vals = (appointment_id,)
        return await exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )

    return None


async def update_appointment_with_scan_vial(appointment_id: int):
    try:
        sql = """
            UPDATE appointments
            SET
                test_start_dt = NOW(),
                status = 'vial_scanned'
            WHERE
                id = %s
        """
        vals = (appointment_id,)
        return await exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )

    return None


async def update_appointment_with_test_completed(appointment_id: int):
    try:
        sql = """
            UPDATE appointments
            SET
                test_end_dt = NOW(),
                status = 'test_completed'
            WHERE
                id = %s
            """
        vals = (appointment_id,)
        return await exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )

    return None


async def get_appointment_count_by_phone_dob(phone_number, dob):
    try:
        if dob:
            sql = """
            SELECT 
                COUNT(*) AS count
            FROM
                appointments a
                    JOIN
                patients p ON (p.id = a.patient_id)
            WHERE
                p.phone_number = %s
                AND p.dob = %s
            """
            vals = (phone_number, dob)

        else:
            sql = """
            SELECT 
                COUNT(*) AS count
            FROM
                appointments a
                    JOIN
                patients p ON (p.id = a.patient_id)
            WHERE
                p.phone_number = %s
            """
            vals = (phone_number,)

        row = await read_row(sql, vals)
        if row:
            return row['count']

    except Exception as err:
        log_generic(
            type=c.ERROR,
            phone_number=phone_number,
            dob=dob,
            function=whoami(),
            error=err
        )

    return 0


async def update_appointment_with_confirmed_scheduled(appointment_id: int):
    return await __update_appointment_status(appointment_id, c.APPOINTMENT_STATUS_SCHEDULED)


async def update_appointment_with_checkin(appointment_id: int):
    return await __update_appointment_status(appointment_id, c.APPOINTMENT_STATUS_CHECKED_IN)


async def update_appointment_with_test_start(appointment_id: int):
    return await __update_appointment_status(appointment_id, c.APPOINTMENT_STATUS_TEST_IN_PROGRESS)


async def update_appointment_with_scan_vial(appointment_id: int):
    return await __update_appointment_status(appointment_id, c.APPOINTMENT_STATUS_VIAL_SCANNED)


async def update_appointment_with_test_completed(appointment_id: int):
    return await __update_appointment_status(appointment_id, c.APPOINTMENT_STATUS_TEST_COMPLETED)

########################################################################################################
# [Protected] functions
########################################################################################################


async def __update_appointment_status(appointment_id: int, status: str):
    try:
        sql = """
            UPDATE appointments
            SET
                test_end_dt = NOW(),
                status = %s
            WHERE
                id = %s
            """
        vals = (status, appointment_id)
        return await exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=appointment_id,
            status=status,
            function=whoami(),
            error=err
        )

    return None


def __map_row_to_appointment(row: dict):
    try:
        l = GgtLocation()
        l.id = row['location_id']
        l.addr1 = row['location_addr1']
        l.addr2 = row['location_addr2']
        l.city = row['location_city']
        l.st = row['location_st']
        l.zip = row['location_zip']
        l.lat = row['lat']
        l.lng = row['lng']

        p = GgtPatient()
        p.id = row['patient_id']
        p.dob = row['patient_dob']
        p.first_name = row['patient_first_name']
        p.middle_name = row['patient_middle_name']
        p.last_name = row['patient_last_name']
        p.addr1 = row['patient_addr1']
        p.addr2 = row['patient_addr2']
        p.city = row['patient_city']
        p.st = row['patient_st']
        p.zip = row['patient_zip']
        p.phone_number = row['patient_phone_number']
        p.email = row['email']
        p.gender = row['gender']
        p.dob = row['dob']

        a = GgtAppointment()
        a.id = row['id']
        a.location_id = row['location_id']
        a.scheduled_dt = row['scheduled_dt']
        a.group_code = row['group_code']
        a.patient_id = row['patient_id']
        a.patient_questionnaire_id = row['patient_questionnaire_id']

        a.check_in_dt = row['check_in_dt']
        a.test_start_dt = row['test_start_dt']
        a.test_end_dt = row['test_end_dt']

        a.wp_customer_info_id = row['wp_customer_info_id']
        a.total_cost = row['total_cost']
        a.billed_amount = row['billed_amount']
        a.wp_receipt_token = row['wp_receipt_token']

        with suppress(AttributeError):
            a.service_selection_codes = row['service_codes'].split(',')
            a.service_selection = row['service_descriptions'].split(',')

        a.location = l
        a.patient = p
        a.status = row['status']

        a.date_text = a.scheduled_dt.strftime(
            "%a, %-d %b %Y @ %-I:%M %p")
        # e.g. 6155 Sports Village Rd, Frisco, TX 75033
        a.location_text = "{}, {} {}  {}".format(
            l.addr1,
            l.city,
            l.st,
            l.zip
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=row,
            function=whoami(),
            error=err
        )

    return a


async def __add_services_to_appointment(appointment_id: int, appointment_req: GgtBooking) -> bool:
    try:
        if appointment_req.service_covid19_test:
            await add_service_to_appointment(appointment_id, c.SERVICE_CODE_COVID19_TEST)

        if appointment_req.service_flu_shot:
            await add_service_to_appointment(appointment_id, c.SERVICE_CODE_FLU_SHOT)

        if appointment_req.service_consult:
            await add_service_to_appointment(appointment_id, c.SERVICE_CODE_CONSULT)

        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            appointment_req=appointment_req,
            error=err
        )
    return False
