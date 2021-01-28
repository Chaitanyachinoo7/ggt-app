from ggt.lib.utils import (
    convert_to_bool,
    log_generic, whoami
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
def create_patient_questionnaire(booking_req):
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
                flu_screen_egg_allergy,
                symptoms_vax,
                pregnancy,
                allergic_reaction,
                covid19_confirmed_case,
                egg_allergy,
                guillian_barre
            )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,  %s, %s, %s, %s, %s, %s)
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
            booking_req.flu_screen_egg_allergy,

            booking_req.symptomsVax,
            booking_req.covid19ConfirmedCase,
            booking_req.pregnancy,
            booking_req.allergicReaction,
            booking_req.eggAllergy,
            booking_req.guillianBarre

        )

        questionnaire_id = exec_insert(sql, vals)
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


def update_patient_questionnaire(req):
    try:
        sql = """
        UPDATE 
            patient_questionnaires
        SET
                symptom_fever = %s, 
                symptom_shortness_breath = %s, 
                symptom_cough = %s, 
                symptom_chest_pain = %s, 
                symptom_lack_of_smell = %s, 
                symptom_other_breathing = %s, 
                covid_contact = %s, 
                prescription_use = %s, 
                heart_disease = %s, 
                diabetes = %s, 
                respiratory_diseases = %s, 
                autoimmune_disease = %s, 
                other_chronic = %s, 
                allergies = %s,  
                public_places_bars_restaurants_cafes  = %s,
                public_places_gas_stations  = %s,
                public_places_medical_offices  = %s,
                public_places_place_of_work = %s,
                public_places_retail_grocery_stores = %s, 
                public_places_places_of_worship = %s,
                public_places_public_parks = %s,
                public_places_other = %s,
                flu_screen_severely_ill = %s,
                flu_screen_guillain_barre_syndrome = %s,
                flu_screen_life_threatening_reaction = %s,
                flu_screen_egg_allergy = %s,
                symptoms_vax = %s,
                pregnancy = %s,
                allergic_reaction = %s,
                covid19_confirmed_case = %s,
                egg_allergy = %s,
                guillian_barre = %s
                WHERE id = %s
        """

        vals = (
        req['symptom_fever'],
        req['symptom_shortness_breath'],
        req['symptom_cough'],
        req['symptom_chest_pain'],
        req['symptom_lack_of_smell'],
        req['symptom_other_breathing'],
        req['covid_contact'],
        req['prescription_use'],
        req['heart_disease'],
        req['diabetes'],
        req['respiratory_diseases'],
        req['autoimmune_disease'],
        req['other_chronic'],
        req['allergies'],
        req['public_places_bars_restaurants_cafes'],
        req['public_places_gas_stations'],
        req['public_places_medical_offices'],
        req['public_places_place_of_work'],
        req['public_places_retail_grocery_stores'],
        req['public_places_places_of_worship'],
        req['public_places_public_parks'],
        req['public_places_other'],
        req['flu_screen_severely_ill'],
        req['flu_screen_guillain_barre_syndrome'],
        req['flu_screen_life_threatening_reaction'],
        req['flu_screen_egg_allergy'],
        req['symptoms_vax'],
        req['pregnancy'],
        req['allergic_reaction'],
        req['covid19_confirmed_case'],
        req['egg_allergy'],
        req['guillian_barre'],
        req['id']
        )

        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=ERROR,
            locals=locals(),
            function=whoami(),
            error=err
        )
        return None
