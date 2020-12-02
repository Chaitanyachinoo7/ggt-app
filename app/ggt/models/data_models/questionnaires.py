from ggt.lib.utils import (
    convert_to_bool,
    log_generic
)

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows
)

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
async def create_patient_questionnaire(booking_req):
    try:
        sql = """
        INSERT INTO 
            patient_questionnaires
            (
                patient_id, 
                group_code, 
                symptom_fever, 
                symptom_shortness_breath, 
                symptom_cough, 
                symptom_chest_pain, 
                symptom_lack_of_smell, 
                symptom_other_breathing, 
                covid_contact, 
                prescription_use, 
                heart_disease, 
                diabetes, 
                respiratory_diseases, 
                autoimmune_disease, 
                other_chronic, 
                allergies,  
                consent_signature, 
                token,
                has_insurance_photo,
                provider_consent_signature,
                provider_consent_custom_field_1,
                provider_consent_custom_field_2,
                provider_consent_custom_field_3,
                influenza_consent_signature,
                public_places_bars_restaurants_cafes,
                public_places_gas_stations,
                public_places_medical_offices,
                public_places_place_of_work,
                public_places_retail_grocery_stores,
                public_places_places_of_worship,
                public_places_public_parks,
                public_places_other,
                service_covid19_test,
                service_flu_shot,
                service_consult,
                flu_screen_severely_ill,
                flu_screen_guillain_barre_syndrome,
                flu_screen_life_threatening_reaction,
                flu_screen_egg_allergy
            )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        vals = (
            booking_req.patient_id, 
            booking_req.group_code, 
            booking_req.symptom_fever, 
            booking_req.symptom_shortbreath,
            booking_req.symptom_coughing,
            booking_req.symptom_chestpains, 
            booking_req.symptom_lack_of_smell, 
            booking_req.symptom_others, 
            booking_req.covid_contact, 
            booking_req.meds, 
            booking_req.heart_disease,
            booking_req.diabetes, 
            booking_req.respiratory_disease, 
            booking_req.autoimmune_disease, 
            booking_req.other_chronic_disease, 
            booking_req.allergies,  
            booking_req.signature, 
            booking_req.token, 
            booking_req.has_insurance_photo,

            booking_req.consent_provider_signature, 
            booking_req.provider_consent_custom_field_1, 
            booking_req.provider_consent_custom_field_2, 
            booking_req.provider_consent_custom_field_3, 

            booking_req.influenza_consent_signature,
            booking_req.public_places_bars_restaurants_cafes,
            booking_req.public_places_gas_stations,
            booking_req.public_places_medical_offices,
            booking_req.public_places_place_of_work,
            booking_req.public_places_retail_grocery_stores,
            booking_req.public_places_places_of_worship,
            booking_req.public_places_public_parks,
            booking_req.public_places_other,
            booking_req.service_covid19_test,
            booking_req.service_flu_shot,
            booking_req.service_consult,
            booking_req.flu_screen_severely_ill,
            booking_req.flu_screen_guillain_barre_syndrome,
            booking_req.flu_screen_life_threatening_reaction,
            booking_req.flu_screen_egg_allergy
        )

        questionnaire_id = await exec_insert(sql, vals)
        return questionnaire_id 

    except Exception as err:
        log_generic(
            type=ERROR, 
            data=data,
            locals=locals(),
            function=whoami(), 
            error=err
        )
        return None
