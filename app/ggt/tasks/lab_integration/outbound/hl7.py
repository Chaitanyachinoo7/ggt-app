from ggt.models.data_models.hl7 import (
    Message, MSH, MSG, PID, PV1, DG1, ORC, OBR, OBX, IN1, GT1
)

from ggt.lib.storage import (
    get_file_blob
)

import datetime
import base64
import time


class HL7:

    def __init__(self, data):
        self.order = data

    def generate_string(self):
        try:
            hl7_message = Message()
            hl7_message.msh = self.__get_msh(self.order)
            hl7_message.pid = self.__get_pid(self.order)
            hl7_message.pv1 = self.__get_pv1(self.order)
            hl7_message.orc = self.__get_orc(self.order)
            hl7_message.obr = self.__get_obr(self.order)
            hl7_message.dg1 = self.__get_dg1(self.order)
            hl7_message.obx_list = self.__get_obx(self.order)

            if self.order['bill'] == 'DB':
                hl7_message.gt1 = self.__get_gt1(self.order)

            if 'insurance_payer' in self.order:
                hl7_message.in1 = self.__get_in1(self.order)

            return True, str(hl7_message), None
        except Exception as err:
            raise
            return False, None, str(err)

    def __get_msh(self, order):
        dt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        cid = str(int(time.time()))

        location_id = order['sample_collection_location_id']
        if location_id == 2415:
            lab_name = 'MAWD'
        elif location_id == 2473:
            pass  # handled by other workers
        else:
            lab_name = 'AIT'

        return MSH(
            msh_1_field_separator='^~\&',
            msh_2_encoding_characters='',
            msh_3_sending_application='WELLHEALTH',
            msh_4_sending_facility=order['client_site_code'],
            msh_5_receiving_application=lab_name,
            msh_6_receiving_facility=lab_name,
            msh_7_datetime_of_message=order['today_dt'],  # dt,
            msh_9_message_type='ORM^O01',
            msh_10_message_control_id=int(time.time() * 1000),
            msh_11_processing_id='P',
            msh_12_version_id='2.3'
        )

    def __get_pid(self, order):
        return PID(
            pid_1_set_id=1,
            pid_2_patient_id=order['patient_id'],  # External Code
            pid_5_patient_name='{}^{}^^^'.format(
                order['last_name'], order['first_name']),  # Last Name^First Name
            pid_7_date_time_of_birth=order['dob'].replace(
                '-', ''),  # Date of Birth
            pid_8_administrative_sex=order['gender'],  # Gender
            pid_10_race=order['race'],  # Race
            pid_11_patient_address='{}^{}^{}^{}^{}^^^^'.format(
                order['addr1'], order['addr2'], order['city'], order['st'], order['zip']),  # Address^Address2^City^State^Zip Code
            pid_13_phone_number_home=order[
                'phone_number'].replace('+1', ''),  # Phone
            pid_18_patient_account_number='{}^^^P'.format(
                order['patient_id']),
            pid_20_drivers_license_number_patient='',
            pid_22_ethnic_group=order['ethnicity']  # Ethnicity
        )

    def __get_pv1(self, order):
        # Lab3A needs a detailed test location address
        if order["lab_id"] == 4:
            patient_location = '{}^{}^{}^{}^^^^'.format(
                order['test_location_addr'], order['test_location_city'], order['test_location_st'], order['test_location_zip'])
        else:
            patient_location = order['test_location_st']

        # AIT / Healthtrackrx has facilities in Mexico country
        if order["lab_id"] == 1 and order["test_location_country"] == "MX":
            patient_location = "MX"

        return PV1(
            pv1_1_set_id=1,
            pv1_3_assigned_patient_location=patient_location,
            # Physician NPI^Provider Last Name^Provider First name
            pv1_7_attending_doctor='{}^{}^{}'.format(
                order['physician_npi'], 'Khan', 'Samad'),
            pv1_20_financial_class=order['bill']
        )

    def __get_gt1(self, order):
        return GT1(
            gt1_1_set_id_gt1='',
            gt1_3_guarantor_name='{}^{}^^^'.format(
                order['last_name'], order['first_name']),  # Last Name^First Name
            gt1_5_guarantor_address='{}^{}^{}^{}^{}^^^^'.format(
                order['addr1'], order['addr2'], order['city'], order['st'], order['zip']),  # Address^Address2^City^State^Zip Code
            gt1_6_guarantor_ph_num_home=order[
                'phone_number'].replace('+1', ''),  # Phone
            gt1_7_guarantor_ph_num_business='',
            gt1_8_guarantor_datetime_of_birth=order['dob'].replace(
                '-', ''),  # Date of Birth
            gt1_9_guarantor_administrative_sex=order['gender'],  # Gender
            gt1_11_guarantor_relationship='01'
        )

    def __get_orc(self, order):
        return ORC(
            orc_1_order_control='',
            # Client Order Number^
            orc_2_placer_order_number=order['client_order_number'],
            orc_3_filler_order_number='{}^{}'.format(
                order['sample_code'], 'AIT' if order['sample_code'] else ''),  # Sample Code^Lab Vial Owner
            orc_4_placer_group_number='',
            orc_5_order_status='',
            orc_6_response_flag='',
            orc_7_quantitytiming='',
            orc_8_parent_order='',
            # Date of Collection
            orc_9_datetime_of_transaction=order['date_of_collection'],
            orc_10_entered_by='',
            orc_11_verified_by='',
            # Physician NPI^Provider Last Name^Provider First name
            orc_12_ordering_provider='{}^{}^{}'.format(
                order['physician_npi'], 'Khan', 'Samad'),
        )

    def __get_obr(self, order):
        return OBR(
            obr_1_set_id='1',
            # Client Order Number
            obr_2_placer_order_number=order['client_order_number'],
            obr_3_filler_order_number='{}^{}'.format(
                order['sample_code'], 'AIT' if order['sample_code'] else ''),  # Sample Code^Lab Vial Owner
            obr_4_universal_service_identifier='RESPI507^COVID-19 Test',  # Panel Code^Panel Name
            obr_6_requested_datetime='',  # Date of Collection
            obr_7_observation_datetime=order[
                'date_of_collection'],  # Date of Collection
            obr_15_specimen_source='^^^{}'.format(
                order['sample_source']),  # Sample Source
            # Physician NPI^Provider Last Name
            obr_16_ordering_provider='{}^{}^{}'.format(
                order['physician_npi'], 'Khan', 'Samad'),
            obr_17_order_callback_phone_number='4697892595',  # WH Phopne number
            obr_21_filler_field_2='^^^^^^'
        )

    def __get_dg1(self, order):
        return DG1(
            dg1_1_set_id_dg1=1,
            # ICD Code
            dg1_3_diagnosis_code_dg1='Z20.828^Contact with and (suspected) exposure to other viral communicable diseases'
        )

    def __get_obx(self, order):
        obx2 = OBX(
            obx_1_set_id=2,
            obx_2_value_type='ST',
            obx_3_observation_identifier='COVID-PT-1^Is this the patient\'s first COVID-19 test?',
            obx_5_observation_value='{}^{}'.format(
                order['is_first_test'][0:1], order['is_first_test'])
        )

        obx3 = OBX(
            obx_1_set_id=3,
            obx_2_value_type='ST',
            obx_3_observation_identifier='COVID-PT-2^Is the patient employed in healthcare with direct patient contact?',
            obx_5_observation_value='{}^{}'.format(
                order['is_first_test'][0:1], order['is_first_test'])
        )

        obx4 = OBX(
            obx_1_set_id=4,
            obx_2_value_type='ST',
            obx_3_observation_identifier='COVID-PT-3A^Is the patient exhibiting symptoms as defined by the CDC?',
            obx_5_observation_value='{}^{}'.format(
                order['is_first_test'][0:1], order['is_first_test'])
        )

        obx5 = OBX(
            obx_1_set_id=5,
            obx_2_value_type='ST',
            obx_3_observation_identifier='COVID-PT-3B^When was first sign of symptoms? (Blank if no or unknown)',
            obx_5_observation_value=''
        )

        obx6 = OBX(
            obx_1_set_id=6,
            obx_2_value_type='ST',
            obx_3_observation_identifier='COVID-PT-4^Has the patient been hospalized?',
            obx_5_observation_value='{}^{}'.format(
                order['is_hospitalized'][0:1], order['is_hospitalized'])
        )

        obx7 = OBX(
            obx_1_set_id=7,
            obx_2_value_type='ST',
            obx_3_observation_identifier='COVID-PT-5^Has the patient been hospalized in the ICU?',
            obx_5_observation_value='{}^{}'.format(
                order['is_in_icu'][0:1], order['is_in_icu'])
        )
        obx8 = OBX(
            obx_1_set_id=8,
            obx_2_value_type='ST',
            obx_3_observation_identifier='COVID-PT-6^Does the patient reside in congregate care (nursing home, group home, etc.)?',
            obx_5_observation_value='{}^{}'.format(
                order['is_congregate_resident'][0:1], order['is_congregate_resident'])
        )

        obx9 = OBX(
            obx_1_set_id=9,
            obx_2_value_type='ST',
            obx_3_observation_identifier='COVID-PT-7^Is the patient pregnant?',
            obx_5_observation_value='{}^{}'.format(
                order['is_pregnant'][0:1], order['is_pregnant'])
        )

        obx10 = None
        if order['bill'] == 'DB':
            try:
                blob = get_file_blob('ggt-insurance-cards-prod',
                                     '{}.png'.format(order['id']))
                if blob:
                    content = blob.download_as_string()
                    b64content = base64.b64encode(content)

                    obx10 = OBX(
                        obx_1_set_id=10,
                        obx_2_value_type='ED',
                        obx_3_observation_identifier='INSURANCE^{}.png'.format(
                            order['client_order_number']),
                        obx_5_observation_value='^^PNG^Base64^{}'.format(
                            b64content)
                    )
            except Exception as err:
                print(err)

        arr = [obx2, obx3, obx4, obx5, obx6, obx7, obx8, obx9, obx10]
        return arr

    def __get_in1(self, order):
        return IN1(
            in1_1_set_id=1,
            in1_2_insurance_plan_id=order['insurance_member_id'],
            in1_3_insurance_company_id=order['insurance_payer'],
            in1_4_insurance_company_name=order['insurance_payer'],
            in1_8_group_number=order['insurance_group_no'],
            in1_16_name_of_insured='{}^{}^^^'.format(
                order['last_name'], order['first_name'])
        )
