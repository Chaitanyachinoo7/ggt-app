from pydantic import BaseModel
from typing import Dict, List, Optional
from enum import Enum, IntEnum
import datetime


class VerifyPhoneRequest(BaseModel):
    phone_number: str


class ValidateOtpRequest(BaseModel):
    phone_number: str
    otp: str


class Symptoms(BaseModel):
    symptom_fever: bool
    symptom_short_breath: bool
    symptom_cough: bool
    symptom_chest_pains: bool
    symptom_other: bool
    symptom_lack_of_smell: bool


class PatientDetails(BaseModel):
    first_name: str
    middle_name: Optional[str] = ""
    last_name: str
    dob: str


class PatientAddress(BaseModel):
    state: str
    street: str
    city: str
    zip_code: str


class PatientContact(BaseModel):
    email: str


class PatientVitals(BaseModel):
    height: str
    weight: str
    medications: bool


class PreExistingConditions(BaseModel):
    heart_disease: bool
    diabetes: bool
    respiratory_disease: bool
    autoimmune_disease: bool
    other_chronic_disease: bool
    allergies: bool


class Consent(BaseModel):
    full_name: str


class ConsentProvider(BaseModel):
    full_name: str


class InfluenzaConsent(BaseModel):
    full_name: str


class PublicPlaces(BaseModel):
    bars_restaurants_cafes: bool
    gas_stations: bool
    medical_offices: bool
    place_of_work: bool
    retail_grocery_stores: bool
    places_of_worship: bool
    public_parks: bool
    other: bool


class ServiceSelection(BaseModel):
    COVID_19_TEST: bool
    CONSULT: bool
    FLU_SHOT: bool


class InfluenzaScreening(BaseModel):
    severely_ill: bool
    guillain_barre_syndrome: bool
    life_threatening_reaction: bool
    egg_allergy: bool


class FinalizeRegistrationRequest(BaseModel):
    groupCode: str
    phone_number: str
    token: str
    isPatient: bool
    gender: str
    race: str
    ethnicity: str
    symptoms: Symptoms
    contactTracing: bool
    patientDetails: PatientDetails
    patientAddress: PatientAddress
    patientContact: PatientContact
    patientVitals: PatientVitals
    preExistingConditions: PreExistingConditions
    insurancePhoto: Optional[str] = None
    consent: Optional[Consent] = None
    provider_consent: Optional[ConsentProvider] = None
    influenza_consent: Optional[InfluenzaConsent] = None
    #location_services = Optional[List[str]] = None
    service_selection: Optional[ServiceSelection] = None
    influenza_screening: Optional[InfluenzaScreening] = None
    public_places: Optional[PublicPlaces] = None
    date: Optional[str] = None
    location: Optional[int] = None
    timeSlot: Optional[int] = None
    hasInsurance: Optional[bool] = None
    forceFinish: Optional[bool] = None


class PhoneData(BaseModel):
    cellphone: str


class FinalizePaymentRequest(BaseModel):
    appointment_id: str
    receipt_token: str


class ValidatePhoneInputRequest(BaseModel):
    phone_number: str


class GetAvailableTimesRequest(BaseModel):
    location_id: str
    dates: str


class ProviderLoginRequest(BaseModel):
    token: str


class ProviderPatientCodeRequest(BaseModel):
    code: str
    token: str


class ProviderUpdateAppointmentRequest(BaseModel):
    appointment_id: str
    auth_token: str
    action: str
    workstation_id: int


class ProviderLookupAppointmentRequest(BaseModel):
    appointment_id: str
    token: str


class PortalLoginRequest(BaseModel):
    token: str


class PortalUserRoleRequest(BaseModel):
    email: str


class ProviderGetMonthlyCalendarRequest(BaseModel):
    date: str
    auth_token: str
    location_id: str


class PortalCcPatientSearchRequest(BaseModel):
    auth_token: str
    last_name: str
    dob: str


class PortalCcTestLookupRequest(BaseModel):
    auth_token: str
    test_id: str


class PortalCcPatientLookupRequest(BaseModel):
    last_name: str
    dob: str


class CCSendSMSRequest(BaseModel):
    first_name: str
    token: str
    to_number: str


class CCSendEmailRequest(BaseModel):
    first_name: str
    token: str
    to_email: str


class CCSendNotiRequest(BaseModel):
    first_name: str
    token: str
    to_email: str
    to_number: str


class CCOutboundResultRequest(BaseModel):
    test_id: str
    first_name: str
    test_date: str
    dob: str
    token: str
    to_email: str
    to_number: str
    test_result: str


class CCOutboundResultStatusRequest(BaseModel):
    test_id: str
    first_name: str
    test_date: str
    dob: str
    token: str
    to_email: str
    to_number: str
    test_result: str
    call_status: str


class PortalGeneralSearchRequest(BaseModel):
    auth_token: str
    first_name: str
    middle_name: str
    last_name: str
    dob: str
    phone_number: str
    email: str
    appointment_id: str
    group_code: str
    appointment_date: str
    location_id: str


class PortalLocationSearchRequest(BaseModel):
    account: str
    group_code: str
    site_code: str


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
    appointment_id: str
    dob: str


class ScanLabelRequest(BaseModel):
    appointment_id: str


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
    provider_consent_signature:  str = None
    influenza_consent_signature:  str = None

    service_covid19_test:  bool = False
    service_flu_shot:  bool = False
    service_consult:  bool = False

    flu_screen_severely_ill:  bool = False
    flu_screen_guillain_barre_syndrome:  bool = False
    flu_screen_life_threatening_reaction:  bool = False
    flu_screen_egg_allergy:  bool = False

    public_places_bars_restaurants_cafes: bool = False
    public_places_gas_stations:  bool = False
    public_places_medical_offices:  bool = False
    public_places_place_of_work:  bool = False
    public_places_retail_grocery_stores:  bool = False
    public_places_places_of_worship:  bool = False
    public_places_public_parks:  bool = False
    public_places_other: bool = False

    insurance_photo: str = None

    date: datetime.date = None
    location: int = None
    time_slot: int = None

    patient_id: int = None


class GgtAppointment(BaseModel):
    id: int = None
    scheduled_dt: datetime.datetime = None
    check_in_dt: datetime.datetime = None
    location_id: int = None
    group_code: str = None
    patient_id: int = None
    patient_questionnaire_id: int = None
    test_start_dt: datetime.datetime = None
    test_end_dt: datetime.datetime = None
    wp_receipt_token: str = None
    wp_customer_info_id: int = None
    total_cost: float = None
    billed_amount: float = None
    status: str = None
    location_text: str = None
    payment_url: str = None
    

class GenderEnum(str, Enum):
    male = 'male'
    female = 'female'
    unknown = 'unknown'


class GgtPatient(BaseModel):
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
    group_code: str = None
    account: str = None
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
    test_covid19: bool = None
    test_flu: bool = None
    test_consult: bool = None
