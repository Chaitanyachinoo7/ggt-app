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
    read_rows,
    replica_read_row,
    replica_read_rows
)

from ggt.models.data_models.data_types import (
    GgtAppointment,
    GgtBooking,
    GgtLocation,
    GgtPatient
)

from ggt.models.data_models.clinical_test_sample import (
    create_test_sample_from_appointment
)


########################################################################################################
# [Public] functions
########################################################################################################


def create_appointment(appointment_req: GgtBooking, ggv_slot=None):
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
            appointment_req.total_cost / 100,  # cents --> decimal
            appointment_req.billed_amount / 100  # cents --> decimal
        )
        appointment_id = exec_insert(sql, vals)
        __add_services_to_appointment(appointment_id, appointment_req, ggv_slot=ggv_slot)
        return get_appointment(appointment_id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            appointment_req=appointment_req,
            error=err
        )

    return None


def add_service_to_appointment(appointment_id: int, service_code: str) -> bool:
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
        vals = (service_code,)
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


def get_appointment(appointment_id: int) -> GgtAppointment:
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
            p.token,
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
        row = read_row(sql, vals)

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


def get_monthy_calendar(from_date: str, to_date: str, location_id: int):
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
        return read_rows(sql, vals)

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


def positive_result_followup():
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
        return replica_read_row(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )

    return None


def update_appointment_with_receipt_token(appointment: GgtAppointment):
    try:
        sql = """
            UPDATE appointments
            SET
                wp_receipt_token = %s
            WHERE
                id = %s
        """
        vals = (appointment.wp_receipt_token, appointment.id)
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment=appointment,
            function=whoami(),
            error=err
        )

    return None


def update_positive_result_followup(id: int, date_time: datetime):
    try:
        sql = """
            UPDATE positive_result_followup_queue
            SET
                overall_status = %s, update_dt = %s
            WHERE
                test_id = %s
            """

        vals = ("pending", date_time, id)
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            id=id,
            date_time=date_time,
            function=whoami(),
            error=err
        )

    return None


def get_appointment_count_by_phone_dob(phone_number, dob):
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

        row = replica_read_row(sql, vals)
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


def update_appointment_with_confirmed_scheduled(appointment: GgtAppointment):
    return __update_appointment_status(appointment, c.APPOINTMENT_STATUS_SCHEDULED)


def update_appointment_with_checkin(appointment: GgtAppointment, user):
    return __update_appointment_status(appointment, c.APPOINTMENT_STATUS_CHECKED_IN, user=user)


def update_appointment_with_start_vax(appointment: GgtAppointment, user, workstation_id):
    return __update_appointment_status(appointment, c.APPOINTMENT_ACTION_START_VAX, user=user,
                                       workstation_id=workstation_id)


def update_appointment_with_verify_insurance(appointment: GgtAppointment, user):
    return __update_appointment_status(appointment, c.APPOINTMENT_ACTION_VERIFY_INSURANCE, user=user)


def update_appointment_with_end_vax(appointment: GgtAppointment, user, workstation_id):
    return __update_appointment_status(appointment, c.APPOINTMENT_ACTION_END_VAX, user=user,
                                       workstation_id=workstation_id)


def update_appointment_with_notes_vax(appointment: GgtAppointment, user, workstation_id):
    return __update_appointment_status(appointment, c.APPOINTMENT_ACTION_NOTES_VAX, user=user,
                                       workstation_id=workstation_id)


def update_appointment_with_test_start(user, appointment: GgtAppointment, workstation_id):
    return __update_appointment_status(appointment, c.APPOINTMENT_STATUS_TEST_IN_PROGRESS, user=user,
                                       workstation_id=workstation_id)


def update_appointment_with_scan_vial(appointment: GgtAppointment, vial_id: str, user):
    return __update_appointment_status(appointment, c.APPOINTMENT_STATUS_VIAL_SCANNED, vial_id, user=user)


def update_appointment_with_scan_vial_vax(appointment: GgtAppointment, vial_id: str, user):
    return __update_appointment_status(appointment, c.APPOINTMENT_ACTION_SCAN_VIAL_VAX, vial_id, user=user)


def update_appointment_with_test_completed(appointment: GgtAppointment, user):
    return __update_appointment_status(appointment, c.APPOINTMENT_STATUS_TEST_COMPLETED, user=user)


def get_service_type_by_appointment_id(appointment_id):
    sql = """SELECT 
                    (CASE
                        WHEN
                            c.service_code LIKE '%VACCINE%'
                        THEN
                             "vax"
                        ELSE "test"
                    END) AS appointment_type
                FROM
                    appointments a
                        JOIN
                    appointment_services s ON a.id = s.appointment_id
                        JOIN
                    services_catalog c ON s.service_id = c.id
                WHERE
                    a.id = %s"""
    vals = (appointment_id, )
    return replica_read_row(sql, vals)

########################################################################################################
# [Protected] functions
########################################################################################################


def __get_mapped_dt_field(status: str) -> str:
    switcher = {
        c.APPOINTMENT_STATUS_SCHEDULED: 'update_dt',
        c.APPOINTMENT_STATUS_CHECKED_IN: 'check_in_dt',
        c.APPOINTMENT_STATUS_TEST_IN_PROGRESS: 'test_start_dt',
        c.APPOINTMENT_STATUS_VIAL_SCANNED: 'test_start_dt',
        c.APPOINTMENT_ACTION_VERIFY_INSURANCE: 'test_start_dt',
        c.APPOINTMENT_ACTION_START_VAX: 'vax_start_dt',
        c.APPOINTMENT_ACTION_SCAN_VIAL_VAX: 'vax_start_dt',
        c.APPOINTMENT_ACTION_END_VAX: 'vax_end_dt',
        c.APPOINTMENT_ACTION_NOTES_VAX: 'vax_notes_dt',
        c.APPOINTMENT_STATUS_TEST_COMPLETED: 'test_end_dt'
    }
    dt_field = switcher.get(status, None)

    if dt_field is None:
        raise ValueError('Invalid Status: {}'.format(status))

    return dt_field


def __update_appointment_status(appointment: GgtAppointment, status: str, vial_id: str = None, user=None, workstation_id=None):
    vial_id = None if vial_id == '' else vial_id
    usuccess = False

    try:
        # Check if a vial has already been assigned, if so, don't allow update to proceed
        if appointment.vial_id and vial_id:
            print('vial has already been assigned')
            return usuccess

        if vial_id:
            #check if vial is a dupe
            sql = """
                SELECT COUNT(*) as count FROM appointments WHERE vial_id = %s
            """
            vals = (vial_id,)
            row = replica_read_row(sql,vals)

            if row['count'] > 0:
                print('duplicate vial ID')
                return usuccess

            #proceed with updating vial_id
            sql = """
                UPDATE appointments
                SET
                    {} = NOW(),
                    update_dt = NOW(),
                    vial_id = %s,
                    status = %s
                WHERE
                    id = %s
                """.format(__get_mapped_dt_field(status))

            vals = (vial_id, status, appointment.id)

        else:
            #proceed with updating other info
            sql = """
                UPDATE appointments
                SET
                    {} = NOW(),
                    update_dt = NOW(),
                    status = %s
                WHERE
                    id = %s
                """.format(__get_mapped_dt_field(status))

            vals = (status, appointment.id)

        usuccess = exec_update(sql, vals)
        __create_provider_appointment_activity(user, appointment.id, whoami(), status, vial_id=vial_id, workstation_id=workstation_id)

        if usuccess and (status == c.APPOINTMENT_STATUS_TEST_COMPLETED or status == c.APPOINTMENT_STATUS_VIAL_SCANNED):
            return create_test_sample_from_appointment(appointment.id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=appointment.id,
            status=status,
            function=whoami(),
            error=err
        )

    return usuccess


def __has_insurance_info(patient_id):
    sql = """SELECT * FROM ggt_prod.patient_questionnaires WHERE patient_id = %s;"""
    vals = (patient_id, )
    row = replica_read_row(sql, vals)
    if row['has_insurance_photo'] == 1:
        return True
    else:
        return False


def __create_provider_appointment_activity(user, appointment_id, function, status, vial_id=None, workstation_id=None):
    try:
        if user:
            user_ext_id = user['sub']
            sql = """INSERT INTO provider_appointment_activity_history
                        (
                            appointment_id,
                            provider_ext_id,
                            function,
                            status,
                            vial_id,
                            workstation_id
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, %s)"""

            vals = (appointment_id, user_ext_id, function, status, vial_id, workstation_id)
            return exec_insert(sql, vals)
        else:
            return None
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def __map_row_to_appointment(row: dict) -> GgtAppointment:
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

        a.vial_id = row['vial_id']

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


def __add_services_to_appointment(appointment_id: int, appointment_req: GgtBooking, ggv_slot=None) -> bool:
    try:
        if appointment_req.service_covid19_vaccine:
            vaccine_service_code = __get_vaccine_service_code_for_location(
                appointment_req.location_id,
                ggv_slot=ggv_slot
            )
            add_service_to_appointment(appointment_id, vaccine_service_code)

        if appointment_req.service_covid19_test:
            add_service_to_appointment(appointment_id, c.SERVICE_CODE_COVID19_TEST)

        if appointment_req.service_flu_shot:
            add_service_to_appointment(appointment_id, c.SERVICE_CODE_FLU_SHOT)

        if appointment_req.service_consult:
            add_service_to_appointment(appointment_id, c.SERVICE_CODE_CONSULT)

        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            appointment_req=appointment_req,
            error=err
        )
    return False


def __get_vaccine_service_code_for_location(location_id, ggv_slot):
    try:
        sql = """
            SELECT
                sc.service_code as service_code
            FROM
                ggt_prod.services_to_locations_mapping sl
                    LEFT JOIN
                ggt_prod.services_catalog sc ON (sl.service_id = sc.id)
            WHERE
                location_id = %s
                    AND sc.service_code like '%VACCINE%{}'
        """.format(ggv_slot)

        vals = (location_id,)
        row = replica_read_row(sql, vals)

        if not row:
            raise ValueError('No Service Info')

        return row['service_code']

    except Exception as err:
        log_generic(
            type=c.ERROR,
            appointment_id=appointment_id,
            function=whoami(),
            error=err
        )

    return None
