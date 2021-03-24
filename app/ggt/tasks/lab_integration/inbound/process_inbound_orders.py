from ggt.tasks.lab_integration.inbound import inbound_utils as inbound
from ggt.tasks.lab_integration import utils

from ggt.lib.utils import (
    get_config_val as cfg,
    print_header,
    print_ok1,
    print_warning,
    print_error
)


def task_process_inbound_results(batch_size=100):
    """
    Send orders to labs
    """

    utils.set_lab_map()
    print_header("START: Inbound Result Processing")

    total_results = inbound.process_inbound_results()

    print_header(
        "END: Inbound Result Processing: {} results processed".format(total_results))
    return total_results
