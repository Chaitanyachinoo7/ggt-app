import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class LocationToGroupMap(BaseModel):
    location_id: str = None
    group_id: str = None


class LocationToServiceMap(BaseModel):
    location_id: str = None
    service_id: str = None


class LockProviderTask(BaseModel):
    test_id: str
    user_id: str
    appointment_id: str


class UpdateProviderTask(BaseModel):
    test_id: str


class ResolutionCodesEnum(str, Enum):
    neg_with_pmh = 'neg_with_pmh'
    neg_without_pmh = 'neg_without_pmh'
    pos_stable = 'pos_stable'
    pos_unstable = 'pos_unstable'


class ConsultationTypeCodesEnum(str, Enum):
    pre_covid_consultation = 'pre_covid_consultation'
    post_covid_consultation = 'post_covid_consultation'


class CompleteNoteReq(BaseModel):
    consultation_id: str
    note: str
    test_id: str
    consultation_type_code: ConsultationTypeCodesEnum
    resolution_code: ResolutionCodesEnum


class UpdateNoteReq(BaseModel):
    consultation_id: str
    note: str


class CallReq(BaseModel):
    patient_mobile: str
    provider_mobile: str


class BillingStatusEnum(str, Enum):
    pending = 'pending'
    initial_billed_status = 'initial_test_billed'
    post_test_billed_status = 'test_result_billed'
    any = 'any'


class SortEnum(str, Enum):
    desc = 'DESC'
    asc = 'ASC'


class PreConsultationEnum(str, Enum):
    pre_consulted = 1
    not_pre_consulted = 0
    any = 'any'


class ProviderReviewedEnum(str, Enum):
    provider_reviewed = 'completed'
    not_provider_reviewed = 'pending'
    any = 'any'


class AppointmentStatusEnum(str, Enum):
    pending = 'pending'
    cancelled = 'cancelled'
    scheduled = 'scheduled'
    checked_in = 'checked_in'
    pre_consultation_in_progress = 'pre_consultation_in_progress'
    test_in_progress = 'test_in_progress'
    vial_scanned = 'vial_scanned'
    test_completed = 'test_completed'
    record_locked = 'record_locked'
    any = 'any'


class TestStatusEnum(str, Enum):
    ready_to_tx = 'ready_to_tx'
    with_lab = 'with_lab'
    lab_result_received = 'lab_result_received'
    cancelled = 'cancelled'
    any = 'any'


class GetBillingListReq(BaseModel):
    offset: int = 0
    from_dt: str
    to_dt: str
    status: BillingStatusEnum = 'any'
    sort: SortEnum = 'DESC'
    limit: int = 20
    pre_consultation: PreConsultationEnum = 'any'
    provider_reviewed: ProviderReviewedEnum = 'any'
    test_status: TestStatusEnum = 'any'
    appointment_status: AppointmentStatusEnum = 'any'


class User(BaseModel):
    iss: str
    sub: str
    aud: Optional[str] = None
    iat: Optional[str] = None
    exp: Optional[str] = None
    azp: Optional[str] = None
    scope: Optional[str] = None
    roles: Optional[str] = None


class ConsultationStatusEnum(str, Enum):
    pending = 'pending'
    in_progress = 'in_progress'
    completed = 'completed'
    any = 'any'


class PositiveCall(str, Enum):
    must_call = 'must_call'
    already_called = 'already_called'
    any = 'any'


class UpdateBilligStatus(BaseModel):
    appointment_id: str


class ConsultationNotesEnum(str, Enum):
    with_notes = 'with_notes'
    without_notes = 'without_notes'
    any = 'any'


class TestResultsEnum(str, Enum):
    pos = 'pos'
    neg = 'neg'
    inconclusive = 'inconclusive'


class ProviderProcessListRequest(BaseModel):
    limit: Optional[int] = 20
    offset: int
    consultation_status: Optional[ConsultationStatusEnum] = None
    consultation_notes: Optional[ConsultationNotesEnum] = None
    positive_call: Optional[PositiveCall] = None


class VerifyPhoneRequest(BaseModel):
    phone_number: str = None
    has_sms: bool = True


class ValidateOtpRequest(BaseModel):
    phone_number: str = None
    otp: str = None


class Symptoms(BaseModel):
    symptom_fever: bool = None
    symptom_short_breath: bool = None
    symptom_cough: bool = None
    symptom_chest_pains: bool = None
    symptom_other: bool = None
    symptom_lack_of_smell: bool = None


class PatientDetails(BaseModel):
    first_name: str = None
    middle_name: Optional[str] = ''
    last_name: str = None
    dob: str = None


class PatientAddress(BaseModel):
    state: str = None
    street: str = None
    city: str = None
    zip_code: str = None


class PatientContact(BaseModel):
    email: str = None


class PatientVitals(BaseModel):
    height: str = None
    weight: str = None
    medications: bool = None


class PreExistingConditions(BaseModel):
    heart_disease: bool = None
    diabetes: bool = None
    respiratory_disease: bool = None
    autoimmune_disease: bool = None
    other_chronic_disease: bool = None
    allergies: bool = None


class Consent(BaseModel):
    full_name: str = None


class ConsentProvider(BaseModel):
    full_name: str = None
    provider_consent_custom_field_1: Optional[str] = None
    provider_consent_custom_field_2: Optional[str] = None
    provider_consent_custom_field_3: Optional[str] = None


class InfluenzaConsent(BaseModel):
    full_name: str = None


class PublicPlaces(BaseModel):
    bars_restaurants_cafes: bool = None
    gas_stations: bool = None
    medical_offices: bool = None
    place_of_work: bool = None
    retail_grocery_stores: bool = None
    places_of_worship: bool = None
    public_parks: bool = None
    other: bool = None


class ServiceSelection(BaseModel):
    COVID_19_TEST: Optional[bool]
    CONSULT: Optional[bool]
    FLU_SHOT: Optional[bool]


class GgtServiceCatalogItem(BaseModel):
    id: int = None
    service_code: str = None
    service_name: str = None
    price: float = None
    selfpay_amount: float = None
    copay_amount: float = None
    insurance_amount: float = None
    sku: str = None
    cost: int = None


class InfluenzaScreening(BaseModel):
    severely_ill: bool = None
    guillain_barre_syndrome: bool = None
    life_threatening_reaction: bool = None
    egg_allergy: bool = None


class FinalizeRegistrationRequest(BaseModel):
    groupCode: str = None
    phone_number: str = None
    token: str = None
    isPatient: bool = None
    gender: str = None
    race: str = None
    ethnicity: str = None
    symptoms: Symptoms = None
    contactTracing: Optional[bool]
    patientDetails: PatientDetails = None
    patientAddress: PatientAddress = None
    patientContact: PatientContact = None
    patientVitals: PatientVitals = None
    preExistingConditions: PreExistingConditions = None
    insurancePhoto: Optional[str] = None
    consent: Optional[Consent] = None
    consent_provider: Optional[ConsentProvider] = None
    influenzaConsent: Optional[InfluenzaConsent] = None

    serviceSelection: Optional[ServiceSelection] = None
    influenzaScreening: Optional[InfluenzaScreening] = None
    publicPlaces: Optional[PublicPlaces] = None
    date: Optional[str] = None
    location: Optional[int] = None
    timeSlot: Optional[int] = None
    hasInsurance: Optional[bool] = None
    forceFinish: Optional[bool] = None


class PhoneData(BaseModel):
    cellphone: str = None


class FinalizePaymentRequest(BaseModel):
    appointment_id: str = None
    receipt_token: str = None


class ValidatePhoneInputRequest(BaseModel):
    phone_number: str = None


class GetAvailableTimesRequest(BaseModel):
    location_id: str = None
    dates: str = None


class ProviderLoginRequest(BaseModel):
    token: str = None


class ProviderPatientCodeRequest(BaseModel):
    code: str = None
    token: str = None


class ProviderUpdateAppointmentRequest(BaseModel):
    appointment_id: str = None
    action: str = None
    workstation_id: int = None
    vial_id: Optional[str] = None


class ProviderLookupAppointmentRequest(BaseModel):
    appointment_id: str = None


class PortalLoginRequest(BaseModel):
    token: str = None


class PortalUserRoleRequest(BaseModel):
    email: str = None


class ProviderGetMonthlyCalendarRequest(BaseModel):
    date: str = None
    location_id: str = None


class PortalCcPatientSearchRequest(BaseModel):
    last_name: str = None
    dob: str = None


class PortalCcTestLookupRequest(BaseModel):
    test_id: str = None


class PortalCcPatientLookupRequest(BaseModel):
    last_name: str = None
    dob: str = None


class CCSendSMSRequest(BaseModel):
    first_name: str = None
    token: str = None
    to_number: str = None


class CCSendEmailRequest(BaseModel):
    first_name: str = None
    token: str = None
    to_email: str = None


class CCSendNotiRequest(BaseModel):
    first_name: str = None
    token: str = None
    to_email: str = None
    to_number: str = None


class CCOutboundResultRequest(BaseModel):
    test_id: str = None
    first_name: str = None
    test_date: str = None
    dob: str = None
    token: str = None
    to_email: str = None
    to_number: str = None
    test_result: str = None


class CCOutboundResultStatusRequest(BaseModel):
    test_id: str = None
    first_name: str = None
    test_date: str = None
    dob: str = None
    token: str = None
    to_email: str = None
    to_number: str = None
    test_result: str = None
    call_status: str = None


class PortalGeneralSearchRequest(BaseModel):
    first_name: str = None
    middle_name: str = None
    last_name: str = None
    dob: str = None
    phone_number: str = None
    email: str = None
    appointment_id: str = None
    group_code: str = None
    appointment_date: str = None
    location_id: str = None
    vial_id: str = None
    sort_field: str = "register_dt"
    sort_type: str = "desc"


class PortalLocationSearchRequest(BaseModel):
    account: str
    group_code: str
    site_code: str
    location_name: str


class ScheduleGenerationRule(BaseModel):
    id: Optional[int] = None
    rule_type: Optional[str] = 'regular'
    time_zone: Optional[str] = None
    time_zone_offset: Optional[str] = None
    status: Optional[str] = 'enabled'
    location_id: int
    slot_increment: Optional[int] = 10
    slot_multiplier: Optional[int] = 1
    local_start_time: Optional[datetime.time] = '12:00:00'
    local_end_time: Optional[datetime.time] = '12:00:00'
    active_local_start_dt: Optional[datetime.datetime] = '2020-01-01 00:00:00'
    active_local_end_dt: Optional[datetime.datetime] = '2020-01-01 00:00:00'
    sun: Optional[bool] = False
    mon: Optional[bool] = False
    tue: Optional[bool] = False
    wed: Optional[bool] = False
    thu: Optional[bool] = False
    fri: Optional[bool] = False
    sat: Optional[bool] = False


class LookupAppointmentRequest(BaseModel):
    appointment_id: str = None
    dob: str = None


class NotificationEnum(str, Enum):
    relocate = 'relocate'
    reschedule = 'reschedule'


class PatientRelocateNotificationRequest(BaseModel):
    location_id: str
    start_dt: str
    end_dt: str
    type: NotificationEnum = 'relocate'
    next_location_id: str


class PatientRescheduleNotificationRequest(BaseModel):
    location_id: str
    start_dt: str
    end_dt: str
    type: NotificationEnum = 'reschedule'


class ScanLabelRequest(BaseModel):
    appointment_id: str = None


class SummaryByDate(BaseModel):
    date: str


class GenderEnum(str, Enum):
    male = 'male'
    female = 'female'
    unknown = 'unknown'


class PermissionsEnum(str, Enum):
    GET_WORKSTATIONS = 'get_workstations'
    LOOKUP_APPOINTMENT = 'lookup_appointment'
    UPDATE_APPOINTMENT = 'update_appointment'
    SCAN_LABEL = 'scan_label'
    PROCESS_INBOUND_LAB_REPORTS = 'process_inbound_lab_reports'
    PROCESS_PROCESS_OUTBOUND_LAB_ORDERS = 'process_process_outbound_lab_orders'
    PROCESS_VOICE_QUEUE = 'process_voice_queue'
    PROCESS_EMAIL_QUEUE = 'process_email_queue'
    PROCESS_SMS_QUEUE = 'process_sms_queue'
    POPULATE_LOCATION_THUMBNAILS = 'populate_location_thumbnails'
    MISC_PROCESSOR = 'misc_processor'
    CREATE_LOCATION = 'create_location'
    CREATE_GROUP = 'create_group'
    UPDATE_GROUP = 'update_group'
    ASSIGN_GROUP = 'assign_group'
    REMOVE_SERVICE = 'remove_service'
    ASSIGN_SERVICE = 'assign_service'
    REMOVE_GROUPS = 'remove_groups'
    GET_LOCATIONS = 'get_locations'
    UPDATE_LOCATION = 'update_location'
    GET_ALL_GROUPS = 'get_all_groups'
    GET_ALL_SERVICES = 'get_all_services'
    GENERAL_SEARCH = 'general_search'
    GENERATE_SCHEDULE = 'generate_schedule'
    GENERATE_ALL_SCHEDULES = 'generate_all_schedules'
    LOCATION_SEARCH = 'location_search'
    ADD_SCHEDULE_GENERATION_RULE = 'add_schedule_generation_rule'
    EDIT_SCHEDULE_GENERATION_RULE = 'edit_schedule_generation_rule'
    DELETE_SCHEDULE_GENERATION_RULE = 'delete_schedule_generation_rule'
    DELETE_SCHEDULE = 'delete_schedule'
    GET_SCHEDULE_GENERATION_RULES = 'get_schedule_generation_rules'
    PATIENT_LOOKUP = 'patient_lookup'
    GET_ALL_TEST_RESULTS = 'get_all_test_results'
    SENDSMS = 'sendsms'
    SENDEMAIL = 'sendemail'
    SMS_EMAIL_NOTIFY = 'sms_email_notify'
    OUTBOUND_RESULT = 'outbound_result'
    OUTBOUND_RESULT_STATUS = 'outbound_result_status'
    ANONYMOUS = 'anonymous'
    PRINTER_QUEUE_CHECK = 'printer_queue_check'
    PRINTER_GET_NEXT_LABEL = 'printer_get_next_label'
    SCHEDULE_RESULT_NOTIFICATIONS_AND_FOLLOWUPS = 'schedule_result_notifications_and_followups'
    PROVIDER_ROLLBACK_TO_PENDING_TASK = 'provider_rollback_to_pending_task'
    PROVIDER_COMPLETE_TASK = 'provider_complete_task'
    UPDATE_CONSULTATION_NOTE = 'update_consultation_note'
    LOCK_PROVIDER_TASK = 'lock_provider_task'
    GET_PROVIDER_PROCESSING_LIST = 'get_provider_processing_list'
    GET_BILLING_LIST = 'get_billing_list'
    UPDATE_BILLING_STATUS = 'update_billing_status'
    CALL_PATIENT = 'call_patient'
    VIEW_INSURANCE_CARD = 'view_insurance_card'
    VIEW_TEST_REPORT = 'view_test_report'
    CREATE_INSURANCE_RECORD = 'create_insurance_record'
    UPDATE_INSURANCE_RECORD = 'update_insurance_record'
    VALIDATE_INSURANCE_RECORD = 'validate_insurance_record'
    DELETE_INSURANCE_RECORD = 'delete_insurance_record'
    ARCHIVE_PROCESSED_NOTIFICATIONS = 'archive_processed_notifications'
    NOTIFY_PATIENTS = 'notify_patients'


class GgtPatient(BaseModel):
    id: int = None
    first_name: str = None
    middle_name: str = None
    last_name: str = None
    addr1: str = None
    addr2: str = None
    addr3: str = None
    city: str = None
    st: str = None
    zip: str = None
    gender: GenderEnum = None
    height_ft: str = None
    height_in: str = None
    weight_lb: str = None
    ethnicity: str = None
    race: str = None
    dob: str = None
    phone_number: str = None
    phone_number_verified: bool = None
    email: str = None
    email_verified: bool = None
    token: str = None


class GgtScheduleSlot(BaseModel):
    id: int = None
    location_id: int = None
    start_dt: datetime.datetime = None
    end_dt: datetime.datetime = None
    duration: int = None
    status: str = None
    appointment_id: int = None


class GgtLocation(BaseModel):
    id: int = None
    site_code: str = None
    name: str = None
    addr1: str = None
    addr2: str = None
    addr3: str = None
    city: str = None
    st: str = None
    zip: str = None
    lat: float = None
    lng: float = None
    time_zone: str = None
    time_zone_offset: str = None
    test_type_offered: str = None
    status: str = None
    type: str = None
    billing_type: str = None
    collect_insurance_info: bool = None
    allow_insurance_skip: bool = None
    collect_upfront_payment: bool = None
    image_thumbnail: str = None
    accepts_bookings: bool = None
    accepts_walkins: bool = None
    operator: str = None
    phone_number: str = None
    website: str = None
    open_hours: str = None
    is_external: bool = False
    services_available: List[GgtServiceCatalogItem] = None


class GgtDbLocation(BaseModel):
    site_code: str = 'GGT'
    group_code: Optional[str] = None
    name: str = None
    addr1: str = None
    addr2: Optional[str] = None
    addr3: Optional[str] = None
    city: str = None
    st: str = 'TX'
    zip: str = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    time_zone: str = 'CST'
    time_zone_offset: str = '-05:00'
    test_type_offered: str = 'oral'
    status: str = 'enabled'
    type: str = 'drive_thru'
    billing_type: str = 'insurance'
    collect_insurance_info: bool = 0
    allow_insurance_skip: bool = 1
    collect_upfront_payment: bool = 0
    image_thumbnail: Optional[str] = None
    accepts_bookings: bool = None
    accepts_walkins: bool = None
    operator: str = None
    phone_number: str = None
    website: str = None
    open_hours: str = None
    is_external: bool = False
    group_ids: List[int] = []
    service_ids: List[int] = []


class GgtUpdateLocation(BaseModel):
    id: str = None
    test_type_offered: str = None
    location_name: str
    status: str = None
    type: str = None
    billing_type: str = None
    collect_insurance_info: str = None
    allow_insurance_skip: str = None
    collect_upfront_payment: str = None
    accepts_bookings: bool = None
    accepts_walkins: bool = None
    operator: str = None
    phone_number: str = None
    website: str = None
    open_hours: str = None
    is_external: bool = False
    group_ids: List[int] = []
    service_ids: List[int] = []


class GgtDateTimeLocation(BaseModel):
    location: GgtLocation = GgtLocation()
    first_date_time_available: datetime.datetime = None
    average_processing_time: float = None
    wait_time: float = None
    slot_count: int = None
    distance: float = None
    is_external: bool = None
    external_phone: str = None
    operated_by: str = None
    accepts_walkins: bool = None
    accepts_bookings: bool = None
    website: str = None
    open_hours: str = None


class GgtBooking(BaseModel):
    token: str = None
    gender: str = None
    dob: datetime.date = None
    height: str = None
    weight: str = None
    ethnicity: str = None
    race: str = None
    phone_number: str = None
    first_name: str = None
    middle_name: str = None
    last_name: str = None
    address: str = None
    city: str = None
    st: str = None
    zip: str = None
    email: str = None

    is_patient: bool = True
    group_code: str = None

    symptom_fever: bool = False
    symptom_shortbreath: bool = False
    symptom_coughing: bool = False
    symptom_chestpains: bool = False
    symptom_others: bool = False
    symptom_lack_of_smell: bool = False

    covid_contact: bool = False

    meds: bool = False
    heart_disease: bool = False
    diabetes: bool = False
    respiratory_disease: bool = False
    autoimmune_disease: bool = False
    other_chronic_disease: bool = False
    allergies: bool = False

    signature: str = None

    consent_provider_signature: str = None
    provider_consent_custom_field_1: str = None
    provider_consent_custom_field_2: str = None
    provider_consent_custom_field_3: str = None

    influenza_consent_signature: str = None

    service_covid19_test: bool = False
    service_flu_shot: bool = False
    service_consult: bool = False

    flu_screen_severely_ill: bool = False
    flu_screen_guillain_barre_syndrome: bool = False
    flu_screen_life_threatening_reaction: bool = False
    flu_screen_egg_allergy: bool = False

    public_places_bars_restaurants_cafes: bool = False
    public_places_gas_stations: bool = False
    public_places_medical_offices: bool = False
    public_places_place_of_work: bool = False
    public_places_retail_grocery_stores: bool = False
    public_places_places_of_worship: bool = False
    public_places_public_parks: bool = False
    public_places_other: bool = False

    insurance_photo: str = None
    has_insurance_photo: bool = None

    date: datetime.date = None
    location_id: int = None
    timeslot_id: int = None
    timeslot: GgtScheduleSlot = None

    patient_id: int = None
    patient_questionnaire_id: int = None
    total_cost: int = None
    billed_amount: int = None

    #language: str = None
    # science37:


'''
class Science37(BaseModel):
    "science37": {
		"participate": true,
		"consent": true,
		"preExistingConditions": true,
		"symptoms": {
			"fever": true,
			"chills": true,
			"muscle_pain": true,
			"joint_pain": true,
			"headache": true,
			"fatigue": true,
			"cough": true,
			"sore_throat": true,
			"nasal_congestion": true,
			"nausea": true,
			"vomiting": true,
			"diarrhea": true,
			"no_symptoms": true
		}
	},
'''


class GgtAppointment(BaseModel):
    id: int = None
    scheduled_dt: datetime.datetime = None
    date_text: str = None
    check_in_dt: datetime.datetime = None
    test_start_dt: datetime.datetime = None
    test_end_dt: datetime.datetime = None

    location_id: int = None
    location_text: str = None
    group_code: str = None
    patient_id: int = None
    patient_questionnaire_id: int = None

    vial_id: str = None

    wp_receipt_token: str = None
    wp_customer_info_id: int = None
    total_cost: float = None
    billed_amount: float = None
    payment_url: str = None

    service_selection_codes: List[str] = None
    service_selection: List[str] = None

    patient: GgtPatient = GgtPatient()
    location: GgtLocation = GgtLocation()

    status: str = None


class GgtTestSample(BaseModel):
    id: int = None
    appointment_id: int = None
    group_code: str = None
    patient_id: int = None
    patient_questionnaire_id: int = None
    provider_id: int = None
    sample_collection_location_id: int = None
    sample_collection_start_dt: datetime.datetime = None
    sample_collection_end_dt: datetime.datetime = None
    pre_ship_label_scan_dt: datetime.datetime = None
    lab_id: int = None
    lab_submission_batch_id: int = None
    lab_physical_submission_dt: datetime.datetime = None
    lab_electronic_submission_dt: datetime.datetime = None
    lab_result_receive_dt: datetime.datetime = None
    test_result: str = None
    notification_status: str = None
    notification_method: str = None
    notification_acknowledgement_dt: datetime.datetime = None
    consultation_status: str = None
    consultation_notes: str = None
    consultation_categorization: str = None
    status: str = None
    test_type: str = None
    appointment: GgtAppointment = GgtAppointment()
    patient: GgtPatient = GgtPatient()
    #patient_questionnaire = GgtPa


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


class GgtCustomField(BaseModel):
    name: str = None
    label: str = None
    required: bool = False


class GgtThirdPartyGroup(BaseModel):
    account_name: str = None
    group_code: str = None
    is_refferal_code: bool = None
    consent_req: bool = None
    collect_insurance: bool = None
    insurance_req: bool = None
    allow_insurance_skip: bool = None
    upfront_payment_req: bool = None
    display_group_consent: bool = None
    intro_text: str = None
    consent_party_name: str = None
    consent_url: str = None
    logo_1: str = None
    logo_2: str = None
    required_screens: List[str] = None
    optional_screens: List[str] = None  # Redundant, remove
    screen_seq: List[str] = None
    additional_fields: List[GgtCustomField] = None


class VerifyExistingPatientRequest(BaseModel):
    phone_number: str = None
    dob: str = None
    # optional_screens: List[str] = None  # Redundant, remove
    #screen_seq: List[str] = None


class GgtThirdPartyDbGroup(BaseModel):
    account: str
    group_code: str
    is_referral_code: int = 0
    billing_type: str = 'insurance'
    consent_req: int = 0
    collect_insurance: int = 0
    insurance_req: int = 0
    allow_insurance_skip: int = 1
    upfront_payment_req: int = 0
    screen_seq: str = None
    optional_screens: str = None
    required_screens: str = None
    display_group_consent: str = None
    consent_party_name: str = None
    consent_url: str = None
    logo_1: str = None
    logo_2: str = None


class GgtThirdPartyDbUpdateGroup(BaseModel):
    id: str
    account: str
    group_code: str
    is_referral_code: int = 0
    billing_type: str = 'insurance'
    consent_req: int = 0
    collect_insurance: int = 0
    insurance_req: int = 0
    allow_insurance_skip: int = 1
    upfront_payment_req: int = 0
    screen_seq: str = None
    optional_screens: str = None
    required_screens: str = None
    display_group_consent: str = None
    consent_party_name: str = None
    consent_url: str = None
    logo_1: str = None
    logo_2: str = None


class InsuranceRecord(BaseModel):
    patient_id: str
    insurance_carrier: str = None
    group_number: str = None
    member_number: str = None
    validated: int = 0


class InsuranceUpdateRecord(BaseModel):
    id: str
    insurance_carrier: str = None
    group_number: str = None
    member_number: str = None
    validated: int = 0


class InsuranceIDRecord(BaseModel):
    id: str


class Base64Image(BaseModel):
    data: str


class InsuranceCardResponse(BaseModel):
    provider: str
    subsriber_name: str
    subsriber_id: str
    group_id: str
    effective_date: str


class InsuranceEligibilityRequest(BaseModel):
    first_name: str = None
    last_name: str = None
    phone_number: str = None
    email: str = None
    dob: str = None
    addr1: str = None
    city: str = None
    state: str = None
    zip_code: str = None
    insurance_id_number: str = None
    insurance_payer_id: str = None
    insurance_group_number: str = None
    level: str = None
