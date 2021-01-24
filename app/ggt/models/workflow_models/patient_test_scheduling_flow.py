from datetime import date
from contextlib import suppress

from cachetools import cached, LRUCache, TTLCache

from ggt.lib.utils import (
    log_generic,
    x_response,
    whoami, y_response
)

from ggt.models.process_models.bp_patient_experience import (
    bp_get_screen_flow_seq,
    bp_initiate_verification_flow,
    bp_validate_phone_number,
    bp_finalize_booking,
    bp_finalize_payment,
    bp_get_test_result, bp_add_to_ggd_waiting_queue,
    bp_get_wellpay_insurance_eligibility,
    bp_search_insurance_payer_list, bp_get_ggv_screen_flow_seq, bp_ggv_finalize_booking
)

from ggt.models.process_models.bp_schedules import (
    bp_get_schedule_dates_available,
    bp_get_schedule_locations_available,
    bp_get_schedule_times_available,
    bp_get_all_available_locations_and_times,
    bp_get_schedule_locations_available_near_lat_lng, bp_ggv_get_schedule_locations_available_near_lat_lng,
    bp_get_second_shot_available_times, bp_get_ggv_schedule_times_available
)

from ggt.models.process_models.bp_appointments import (
    bp_get_appointment_info
)

from ggt.models.data_models.data_types import (
    GgtBooking
)

import ggt.lib.constants as c


########################################################################################################
# [Public] functions
########################################################################################################

@cached(cache=TTLCache(maxsize=1024, ttl=600))
def get_screen_flow_seq(group_code):
    return x_response(
        bp_get_screen_flow_seq(group_code)
    )


@cached(cache=TTLCache(maxsize=1024, ttl=600))
def get_ggv_screen_flow_seq(group_code):
    return x_response(
        bp_get_ggv_screen_flow_seq(group_code)
    )


def initiate_verification_flow(phone_number, with_otp=True):
    return x_response(
        bp_initiate_verification_flow(
            phone_number,
            with_otp
        )
    )


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def validate_phone_number(phone_number, otp):
    return x_response(
        bp_validate_phone_number(
            phone_number,
            otp
        )
    )


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_schedule_dates_available(group_code=c.DEFAULT_GROUP_CODE):
    return x_response(
        bp_get_schedule_dates_available(
            group_code
        )
    )


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def get_schedule_locations_available(group_code, date):
    return x_response(
        bp_get_schedule_locations_available(
            group_code,
            date
        )
    )


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_schedule_locations_available_near_lat_lng(date, group_code, lat, lng, radius):
    return x_response(
        bp_get_schedule_locations_available_near_lat_lng(
            lat,
            lng,
            radius,
            date,
            group_code
        )
    )


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_ggv_schedule_locations_available(group_code, lat, lng, radius):
    return y_response(
        bp_ggv_get_schedule_locations_available_near_lat_lng(group_code, lat, lng, radius)
    )


@cached(cache=TTLCache(maxsize=1024, ttl=120))
def get_all_available_locations_and_times(group_code):
    return x_response(
        bp_get_all_available_locations_and_times(group_code)
    )


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_schedule_times_available(
    location_id,
    date=date.today().strftime("%Y-%m-%d")
):
    return x_response(
        bp_get_schedule_times_available(
            location_id,
            date
        )
    )


def get_ggv_schedule_times_available(
    location_id,
    date=date.today().strftime("%Y-%m-%d")
):
    return x_response(
        bp_get_ggv_schedule_times_available(
            location_id,
            date
        )
    )


def get_second_shot_available_times(req):
    location_id = req.location_id
    if len(req.dates) > 1:
        date = str(tuple((req.dates)))
    elif len(req.dates) == 1:
        date = "('{}')".format(req.dates[0])
    return x_response(
        bp_get_second_shot_available_times(location_id, date)
    )


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def lookup_appointment(appointment_id, dob):
    return x_response(
        bp_get_appointment_info(
            appointment_id,
            dob
        )
    )


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def lookup_test_result(token, dob):
    return x_response(
        bp_get_test_result(
            token,
            dob
        )
    )


def finalize_payment(finalize_payment_request):
    appointment_id = finalize_payment_request.appointment_id
    wp_receipt_token = finalize_payment_request.receipt_token

    if bp_finalize_payment(appointment_id, wp_receipt_token):
        return {c.STATUS: c.SUCCESS}
    else:
        return {c.STATUS: c.FAILED}


def finalize_registration(finalize_registration_request):
    booking_req = __map_to_booking_req(finalize_registration_request)
    appointment, status_message, patient_id = bp_finalize_booking(booking_req)

    if finalize_registration_request.ggd_waitlist:
        bp_add_to_ggd_waiting_queue(patient_id)
    if appointment:
        return {
            "appointment_id": appointment.id,
            "date": appointment.date_text,
            "location": appointment.location_text,
            'total_balance': int(appointment.billed_amount*100),
            'total_cost': int(appointment.total_cost*100),
            'payment_url': appointment.payment_url,
            c.STATUS: c.SUCCESS
        }
    else:
        return {
            c.STATUS: c.FAILED,
            c.ERROR: status_message
        }


def ggv_finalize_registration(finalize_registration_request):
    booking_req = __map_to_booking_req(finalize_registration_request, ggv=True)
    appointment_1, appointment_2, status_message, patient_id = bp_ggv_finalize_booking(booking_req)

    if finalize_registration_request.ggd_waitlist:
        bp_add_to_ggd_waiting_queue(patient_id)
    if appointment_1 and appointment_2:
        return {
            "appointment_id_1": appointment_1.id,
            "date_1": appointment_1.date_text,
            "location_1": appointment_1.location_text,
            'total_balance_1': int(appointment_1.billed_amount*100),
            'total_cost_1': int(appointment_1.total_cost*100),
            'payment_url_1': appointment_1.payment_url,
            "appointment_id_2": appointment_2.id,
            "date_2": appointment_2.date_text,
            "location_2": appointment_2.location_text,
            'total_balance_2': int(appointment_2.billed_amount*100),
            'total_cost_2': int(appointment_2.total_cost*100),
            'payment_url_2': appointment_2.payment_url,
            c.STATUS: c.SUCCESS
        }
    else:
        return {
            c.STATUS: c.FAILED,
            c.ERROR: status_message
        }


def __map_to_booking_req(finalize_registration_request, ggv=False):
    b = GgtBooking()
    try:
        b.token = finalize_registration_request.token
        b.phone_number = finalize_registration_request.phone_number.strip()
        b.first_name = finalize_registration_request.patientDetails.first_name.strip()
        b.middle_name = finalize_registration_request.patientDetails.middle_name.strip()
        b.last_name = finalize_registration_request.patientDetails.last_name.strip()
        b.gender = finalize_registration_request.gender

        b.address = finalize_registration_request.patientAddress.street.strip()
        b.city = finalize_registration_request.patientAddress.city.strip()
        b.zip = finalize_registration_request.patientAddress.zip_code.strip()
        b.email = finalize_registration_request.patientContact.email.strip()

        b.st = finalize_registration_request.patientAddress.state
        b.dob = finalize_registration_request.patientDetails.dob
        b.height = finalize_registration_request.patientVitals.height
        b.weight = finalize_registration_request.patientVitals.weight
        b.ethnicity = finalize_registration_request.ethnicity
        b.race = finalize_registration_request.race

        b.is_patient = finalize_registration_request.isPatient
        b.group_code = finalize_registration_request.groupCode.strip()
        if finalize_registration_request.symptoms:
            b.symptom_fever = finalize_registration_request.symptoms.symptom_fever

            b.symptom_shortbreath = finalize_registration_request.symptoms.symptom_short_breath
            b.symptom_coughing = finalize_registration_request.symptoms.symptom_cough
            b.symptom_chestpains = finalize_registration_request.symptoms.symptom_chest_pains
            b.symptom_others = finalize_registration_request.symptoms.symptom_other
            b.symptom_lack_of_smell = finalize_registration_request.symptoms.symptom_lack_of_smell
        b.covid_contact = finalize_registration_request.contactTracing

        b.meds = finalize_registration_request.patientVitals.medications
        b.heart_disease = finalize_registration_request.preExistingConditions.heart_disease
        b.diabetes = finalize_registration_request.preExistingConditions.diabetes
        b.respiratory_disease = finalize_registration_request.preExistingConditions.respiratory_disease
        b.autoimmune_disease = finalize_registration_request.preExistingConditions.autoimmune_disease
        b.other_chronic_disease = finalize_registration_request.preExistingConditions.other_chronic_disease
        b.allergies = finalize_registration_request.preExistingConditions.allergies

        # if the request comes from GGV, then set the vaccination service
        if ggv:
            b.service_covid19_vaccine = True
        else:
            if finalize_registration_request.serviceSelection:
                b.service_covid19_test = finalize_registration_request.serviceSelection.COVID_19_TEST
                b.service_flu_shot = finalize_registration_request.serviceSelection.FLU_SHOT
                b.service_consult = finalize_registration_request.serviceSelection.CONSULT
            else:
                # handle errors in form submission where there is no test type submitted
                b.service_covid19_test = True

        b.insurance_photo = finalize_registration_request.insurancePhoto
        if b.insurance_photo and len(b.insurance_photo) > 250:
            b.has_insurance_photo = True
        else:
            b.has_insurance_photo = False

        b.date = finalize_registration_request.date
        b.location_id = finalize_registration_request.location
        b.timeslot_id = finalize_registration_request.timeSlot

        if "appointmentOneTime" in finalize_registration_request.fields.keys():
            b.appointmentOneTime = finalize_registration_request.appointmentOneTime
        if "appointmentTwoTime" in finalize_registration_request.fields.keys():
            b.appointmentTwoTime = finalize_registration_request.appointmentTwoTime
        if "symptomsVax" in finalize_registration_request.fields.keys():
            b.symptomsVax = finalize_registration_request.symptomsVax
        if "covid19ConfirmedCase" in finalize_registration_request.fields.keys():
            b.covid19ConfirmedCase = finalize_registration_request.covid19ConfirmedCase
        if "pregnancy" in finalize_registration_request.fields.keys():
            b.pregnancy = finalize_registration_request.pregnancy
        if "allergicReaction" in finalize_registration_request.fields.keys():
            b.allergicReaction = finalize_registration_request.allergicReaction
        if "eggAllergy" in finalize_registration_request.fields.keys():
            b.eggAllergy = finalize_registration_request.eggAllergy
        if "guillianBarre" in finalize_registration_request.fields.keys():
            b.guillianBarre = finalize_registration_request.guillianBarre

        with suppress(AttributeError):
            b.public_places_bars_restaurants_cafes = finalize_registration_request.publicPlaces.bars_restaurants_cafes
            b.public_places_gas_stations = finalize_registration_request.publicPlaces.gas_stations
            b.public_places_medical_offices = finalize_registration_request.publicPlaces.medical_offices
            b.public_places_place_of_work = finalize_registration_request.publicPlaces.place_of_work
            b.public_places_retail_grocery_stores = finalize_registration_request.publicPlaces.retail_grocery_stores
            b.public_places_places_of_worship = finalize_registration_request.publicPlaces.places_of_worship
            b.public_places_public_parks = finalize_registration_request.publicPlaces.public_parks
            b.public_places_other = finalize_registration_request.publicPlaces.other

            b.signature = finalize_registration_request.consent.full_name.strip()
            b.consent_provider_signature = finalize_registration_request.consent_provider.full_name.strip()
            b.provider_consent_custom_field_1 = finalize_registration_request.consent_provider.provider_consent_custom_field_1.strip()
            b.provider_consent_custom_field_2 = finalize_registration_request.consent_provider.provider_consent_custom_field_2.strip()
            b.provider_consent_custom_field_3 = finalize_registration_request.consent_provider.provider_consent_custom_field_3.strip()

            b.influenza_consent_signature = finalize_registration_request.influenzaConsent.full_name.strip()

            b.flu_screen_severely_ill = finalize_registration_request.influenzaScreening.severely_ill
            b.flu_screen_guillain_barre_syndrome = finalize_registration_request.influenzaScreening.guillain_barre_syndrome
            b.flu_screen_life_threatening_reaction = finalize_registration_request.influenzaScreening.life_threatening_reaction
            b.flu_screen_egg_allergy = finalize_registration_request.influenzaScreening.egg_allergy

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            finalize_registration_request=finalize_registration_request,
            error=err
        )

    return b


def insurance_eligibility(insurance_eligibility_request):
    return bp_get_wellpay_insurance_eligibility(insurance_eligibility_request)

def insurance_search_payer(insurance_search_payer_request):
    return bp_search_insurance_payer_list(insurance_search_payer_request)
