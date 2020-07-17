from ggt.lib.utils import (
    convert_to_bool,
    log_generic)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows)


########################################################################################################
# [Public] functions
########################################################################################################


########################################################################################################
# [Protected] functions
########################################################################################################

#TODO: isPatient?
def create_patient_questionnaire(data):
    symptom_fever = convert_to_bool(data["symptom_fever"])
    symptom_shortbreath = convert_to_bool(data["symptom_shortbreath"])
    symptom_coughing = convert_to_bool(data["symptom_coughing"])
    symptom_chestpains = convert_to_bool(data["symptom_chestpains"])
    symptom_others = convert_to_bool(data["symptom_others"])
    symptom_lack_of_smell = convert_to_bool(data["symptom_lack_of_smell"])
    covid_contact = convert_to_bool(data["covid_contact"])

    meds = convert_to_bool(data["meds"])
    heart_disease = convert_to_bool(data["heart_disease"])
    diabetes = convert_to_bool(data["diabetes"])
    respiratory_disease = convert_to_bool(data["respiratory_disease"])
    autoimmune_disease = convert_to_bool(data["autoimmune_disease"])
    other_chronic_disease = convert_to_bool(data["other_chronic_disease"])
    allergies = convert_to_bool(data["allergies"])
    signature = data["signature"]

    patient_id = data["patient_id"]
    token = data["token"]
    group_code = data["group_code"]

    try:
        sql = """
        INSERT INTO patient_questionnaires 
            (patient_id, group_code, symptom_fever, symptom_shortness_breath, symptom_cough, 
            symptom_chest_pain, symptom_lack_of_smell, symptom_other_breathing, covid_contact, 
            prescription_use, heart_disease, diabetes, respiratory_diseases, autoimmune_disease, 
            other_chronic, allergies,  consent_signed, token)
        
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        val = (patient_id, group_code, symptom_fever, symptom_shortbreath, symptom_coughing, 
                symptom_chestpains, symptom_lack_of_smell, symptom_others, covid_contact, meds, heart_disease,
               diabetes, respiratory_disease, autoimmune_disease, other_chronic_disease, allergies,  signature, token)

        return exec_insert(sql, val)

    except Exception as err:
        log_generic(type="error", data=data, locals=locals(),
                    function='create_patient_questionnaire', error=err)
        return None
