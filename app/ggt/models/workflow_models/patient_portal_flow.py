from datetime import date
from contextlib import suppress

from ggt.lib.utils import (
    log_generic,
    x_response,
    whoami
)

from ggt.models.process_models.bp_patient_experience import (
    bp_has_appointments
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR,
    DEFAULT_GROUP_CODE
)

########################################################################################################
# [Public] functions
########################################################################################################


def verify_existing_patient(phone_number, dob):
    return x_response(
        bp_has_appointments(phone_number, dob)
    )
