from starlette.responses import StreamingResponse

from ggt.lib.utils import (
    x_response,
    y_response
)
from ggt.models.process_models.bp_biller_experience import bp_get_billing_list, bp_update_billing_status, \
    bp_image_from_bucket, bp_report_from_bucket, bp_create_insurance_record, bp_update_insurance_record, \
    bp_validate_insurance_record, bp_delete_insurance_record

from ggt.models.process_models.bp_care_provider_experience import (
    bp_get_provider_processing_list, bp_lock_provider_task, bp_create_patient_test_consultation,
    bp_update_consultation_note, bp_provider_complete_task, bp_provider_rollback_to_pending_task)

from ggt.lib.cache import (
    timed_lru_cache
)

########################################################################################################
# [Public] functions
########################################################################################################

def get_billing_list(billing_request):
    return y_response(
        bp_get_billing_list(billing_request.offset,
                            billing_request.status,
                            billing_request.from_dt,
                            billing_request.to_dt,
                            billing_request.limit,
                            billing_request.sort,
                            billing_request.pre_consultation,
                            billing_request.provider_reviewed
                            )
    )


def update_billing_status(billing_request):
    return x_response(
        bp_update_billing_status(billing_request.appointment_id)
    )


def create_insurance_record(record):
    return y_response(
        bp_create_insurance_record(record)
    )


def update_insurance_record(record):
    return y_response(
        bp_update_insurance_record(record)
    )


def validate_insurance_record(record):
    return y_response(
        bp_validate_insurance_record(record)
    )


def delete_insurance_record(record):
    return y_response(
        bp_delete_insurance_record(record)
    )


def get_image_from_bucket(image_id):
    return StreamingResponse(
        bp_image_from_bucket(image_id),
        media_type="image/png",
        headers={
            'Content-Disposition': 'inline; filename="insurance_card.png"'
        }
    )


def get_report_from_bucket(report_id):
    return StreamingResponse(
        bp_report_from_bucket(report_id),
        media_type="application/pdf",
        headers={
            'Content-Disposition': 'filename="report.pdf"'
        }
    )

########################################################################################################
# [Protected] functions
########################################################################################################
