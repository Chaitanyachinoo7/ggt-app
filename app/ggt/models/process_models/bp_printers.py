from ggt.lib.utils import (
    log_generic
)

from ggt.lib.printer_label import (
    generate_label
)

from ggt.models.data_models.printers import (
    get_next_print_job,
    get_all_printer_hubs
)

import ggt.lib.constants as c

def bp_printer_queue_check(printer_id, printer_token):
    pass


def bp_get_next_label(workstation_id, workstation_token):
    d = get_next_print_job(workstation_id, workstation_token)
    if d:
        barcode_text = d['appointment_id']
        timestamp_text = d['scheduled_dt'].strftime("%a, %-d %b %Y @ %-I:%M %p")
        name_text = "{}, {} {}".format(
                                    d['last_name'],
                                    d['first_name'],
                                    d['middle_name'],
                                )
        dob_text = d['dob'].strftime("%m/%d/%Y")

        return generate_label(barcode_text, name_text, dob_text, timestamp_text)
    else:
        return


def bp_provider_get_workstations():
    hub_list = []
    printer_hubs = get_all_printer_hubs()
    for hub in printer_hubs:
        hub_list.append({
            'id': hub['id'],
            'label': hub['label']
        })

    return {
        'workstations': hub_list
    }
