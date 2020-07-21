from datetime import date

from ggt.lib.utils import (
    log_generic,
    x_response
)

from ggt.models.process_models.bp_patient_experience import (
    bp_initiate_verification_flow,
    bp_validate_phone_number,
    bp_finalize_registration,
    bp_finalize_booking,
    bp_finalize_payment,
    bp_get_test_result
)

from ggt.models.process_models.bp_schedules import (
    bp_get_schedule_dates_available,
    bp_get_schedule_locations_available,
    bp_get_schedule_times_available
)

from ggt.models.process_models.bp_appointments import (
    bp_get_appointment_info
)

########################################################################################################
# [Public] functions
########################################################################################################


def get_screen_flow_seq(group_code):
    return x_response({
        "screens": ["is-patient",
                    "gender",
                    "race",
                    "ethnicity",
                    "symptoms",
                    "contact-tracing",
                    "patient-details",
                    "patient-address",
                    "patient-contact",
                    "patient-vitals",
                    "pre-existing-conditions",
                    "insurance-card",
                    "consent",
                    "date",
                    "location",
                    "time"]
    })


def initiate_verification_flow(phone_number, with_otp=True):
    return x_response(
        bp_initiate_verification_flow(
            phone_number,
            with_otp
        )
    )


def validate_phone_number(phone_number, otp):
    return x_response(
        bp_validate_phone_number(
            phone_number,
            otp
        )
    )


def get_schedule_dates_available(group_code='_DEFAULT_'):
    return x_response(
        bp_get_schedule_dates_available(
            group_code
        )
    )


def get_schedule_locations_available(group_code, date):
    return x_response(
        bp_get_schedule_locations_available(
            group_code,
            date
        )
    )


def get_schedule_times_available(location_id, date=date.today().strftime("%Y-%m-%d")):
    return x_response(
        bp_get_schedule_times_available(
            location_id,
            date
        )
    )


def lookup_appointment(appointment_id):
    return x_response(
        bp_get_appointment_info(
            appointment_id
        )
    )


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
        return {"status": "success"}
    else:
        return {'status': 'failed'}



def finalize_registration(finalize_registration_request):
    token = finalize_registration_request.token
    phone_number = finalize_registration_request.phone_number
    first_name = finalize_registration_request.patientDetails.first_name
    middle_name = finalize_registration_request.patientDetails.middle_name
    last_name = finalize_registration_request.patientDetails.last_name
    gender = finalize_registration_request.gender

    address = finalize_registration_request.patientAddress.street
    city = finalize_registration_request.patientAddress.city
    zip = finalize_registration_request.patientAddress.zip_code
    email = finalize_registration_request.patientContact.email

    st = finalize_registration_request.patientAddress.state
    dob = finalize_registration_request.patientDetails.dob
    height = finalize_registration_request.patientVitals.height
    weight = finalize_registration_request.patientVitals.weight
    ethnicity = finalize_registration_request.ethnicity
    race = finalize_registration_request.race

    is_patient = finalize_registration_request.isPatient
    group_code = finalize_registration_request.groupCode
    symptom_fever = finalize_registration_request.symptoms.symptom_fever

    symptom_shortbreath = finalize_registration_request.symptoms.symptom_short_breath
    symptom_coughing = finalize_registration_request.symptoms.symptom_cough
    symptom_chestpains = finalize_registration_request.symptoms.symptom_chest_pains
    symptom_others = finalize_registration_request.symptoms.symptom_other
    symptom_lack_of_smell = finalize_registration_request.symptoms.symptom_lack_of_smell
    covid_contact = finalize_registration_request.contactTracing

    meds = finalize_registration_request.patientVitals.medications
    heart_disease = finalize_registration_request.preExistingConditions.heart_disease
    diabetes = finalize_registration_request.preExistingConditions.diabetes
    respiratory_disease = finalize_registration_request.preExistingConditions.respiratory_disease
    autoimmune_disease = finalize_registration_request.preExistingConditions.autoimmune_disease
    other_chronic_disease = finalize_registration_request.preExistingConditions.other_chronic_disease
    allergies = finalize_registration_request.preExistingConditions.allergies
    signature = finalize_registration_request.consent.full_name

    insurance_photo = finalize_registration_request.insurancePhoto

    date = finalize_registration_request.date
    location = finalize_registration_request.location
    time_slot = finalize_registration_request.timeSlot

    data = {
        'token': token,
        'gender': gender,
        'dob': dob,
        'height': height,
        'weight': weight,
        'ethnicity': ethnicity,
        'race': race,
        'phone_number': phone_number,
        'first_name': first_name,
        'middle_name': middle_name,
        'last_name': last_name,
        'address': address,
        'city': city,
        'st': st,
        'zip': zip,
        'email': email,

        'is_patient': is_patient,
        'group_code': group_code.upper(),

        'symptom_fever': symptom_fever,
        'symptom_shortbreath': symptom_shortbreath,
        'symptom_coughing': symptom_coughing,
        'symptom_chestpains': symptom_chestpains,
        'symptom_others': symptom_others,
        'symptom_lack_of_smell': symptom_lack_of_smell,
        'covid_contact': covid_contact,

        'meds': meds,
        'heart_disease': heart_disease,
        'diabetes': diabetes,
        'respiratory_disease': respiratory_disease,
        'autoimmune_disease': autoimmune_disease,
        'other_chronic_disease': other_chronic_disease,
        'allergies': allergies,
        'signature': signature,

        'insurance_photo': insurance_photo,

        'date': date,
        'location': location,
        'time_slot': time_slot
    }
    #appointment = bp_finalize_registration(data)
    appointment = bp_finalize_booking(data)

    if appointment:
        return {
            "appointment_id": appointment['appointment_id'],
            "date": appointment['date'],
            "location": appointment['location'],
            'total_balance': appointment['total_balance'],
            'total_cost': appointment['total_cost'],
            'payment_url': appointment['payment_url'],
            "status": "success"
        }
    else:
        return {'status': 'failed'}
