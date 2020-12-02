from datetime import date
from contextlib import suppress

from aiocache import cached

from ggt.lib.utils import (
    log_generic,
    x_response,
    whoami
)

from ggt.models.process_models.bp_patient_experience import (
    bp_has_appointments
)

########################################################################################################
# [Public] functions
########################################################################################################

@cached(ttl=600)


async def verify_existing_patient(phone_number, dob):
    return x_response(
        await bp_has_appointments(phone_number, dob)
    )
