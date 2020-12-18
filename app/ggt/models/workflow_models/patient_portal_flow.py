from datetime import date
from contextlib import suppress

from cachetools import cached, LRUCache, TTLCache

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

@cached(cache=TTLCache(maxsize=1024, ttl=600))
def verify_existing_patient(phone_number, dob):
    return x_response(
        bp_has_appointments(phone_number, dob)
    )
