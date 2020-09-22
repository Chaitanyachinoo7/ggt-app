from pydantic import BaseModel
from typing import Dict, List, Optional
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
    consent: Consent
    date: Optional[str] = None
    location: Optional[int] = None
    timeSlot: Optional[int] = None


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
