import io
from fastapi.responses import StreamingResponse, FileResponse

from cachetools import cached, LRUCache, TTLCache

from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response,
    whoami
)

from ggt.models.process_models.bp_printers import (
    bp_printer_queue_check,
    bp_get_next_label
)


########################################################################################################
# [Public] functions
########################################################################################################

def printer_queue_check(workstation_id, workstation_token):
    return x_response(
        bp_printer_queue_check()
    )


def printer_get_next_label(workstation_id, workstation_token):
    return StreamingResponse(
        bp_get_next_label(workstation_id, workstation_token),
        media_type="image/png",
        headers={
            'Content-Disposition': 'inline; filename="new_label.jpg"'
        }
    )

########################################################################################################
# [Protected] functions
########################################################################################################
