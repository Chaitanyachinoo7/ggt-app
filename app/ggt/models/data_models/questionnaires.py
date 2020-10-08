from ggt.lib.utils import (
    convert_to_bool,
    log_generic)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

########################################################################################################
# [Public] functions
########################################################################################################


########################################################################################################
# [Protected] functions
########################################################################################################

# TODO: isPatient?
def create_patient_questionnaire(booking_req):
    '''
    symptom_fever = convert_to_bool(booking_req.symptom_fever)
    symptom_shortbreath = convert_to_bool(booking_req.symptom_shortbreath"])
    symptom_coughing = convert_to_bool(booking_req.symptom_coughing"])
    symptom_chestpains = convert_to_bool(booking_req.symptom_chestpains"])
    symptom_others = convert_to_bool(booking_req.symptom_others"])
    symptom_lack_of_smell = convert_to_bool(booking_req.symptom_lack_of_smell"])
    covid_contact = convert_to_bool(booking_req.covid_contact"])

    is_patient = convert_to_bool(booking_req.is_patient"])

    meds = convert_to_bool(booking_req.meds"])
    heart_disease = convert_to_bool(booking_req.heart_disease"])
    diabetes = convert_to_bool(booking_req.diabetes"])
    respiratory_disease = convert_to_bool(booking_req.respiratory_disease"])
    autoimmune_disease = convert_to_bool(booking_req.autoimmune_disease"])
    other_chronic_disease = convert_to_bool(booking_req.other_chronic_disease"])
    allergies = convert_to_bool(booking_req.allergies"])
    signature = booking_req.signature"]

    patient_id = booking_req.patient_id"]
    token = booking_req.token"]
    group_code = booking_req.group_code"]
    '''
    #insurance_photo = data["insurance_photo"]

    try:
        sql = """
        INSERT INTO patient_questionnaires 
            (patient_id, group_code, symptom_fever, symptom_shortness_breath, symptom_cough, 
            symptom_chest_pain, symptom_lack_of_smell, symptom_other_breathing, covid_contact, 
            prescription_use, heart_disease, diabetes, respiratory_diseases, autoimmune_disease, 
            other_chronic, allergies,  consent_signed, token, insurance_photo)
        
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        vals = (booking_req.patient_id, booking_req.group_code, booking_req.symptom_fever, 
                booking_req.symptom_shortbreath, booking_req.symptom_coughing,
                booking_req.symptom_chestpains, booking_req.symptom_lack_of_smell, booking_req.symptom_others, 
                booking_req.covid_contact, booking_req.meds, booking_req.heart_disease,
                booking_req.diabetes, booking_req.respiratory_disease, booking_req.autoimmune_disease, 
                booking_req.other_chronic_disease, booking_req.allergies,  booking_req.signature, 
                booking_req.token, booking_req.insurance_photo)

        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(type=ERROR, data=data, locals=locals(),
                    function=whoami(), error=err)
        return None
