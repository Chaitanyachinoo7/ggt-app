from ggt.tasks.lab_integration.outbound import outbound_utils as outbound
from ggt.tasks.lab_integration import utils

from ggt.lib.utils import (
    get_config_val as cfg,
    print_header,
    print_ok1,
    print_warning,
    print_error
)


def task_process_outbound_orders(batch_size=100):
    """
    Send orders to labs
    """

    utils.set_lab_map()
    print_header("START: Outbound Order Generation")

    orders_batch = outbound.get_orders_ready_to_transmit(limit=batch_size)
    print_ok1("New orders to be generated: {0}".format(len(orders_batch)))

    processed_orders = outbound.create_outbound_requests(orders_batch)
    outbound.update_to_with_lab_status(processed_orders)

    status_msg = "{0}/{1} orders generated".format(
        len(processed_orders), len(orders_batch))
    if len(processed_orders) < len(orders_batch):
        print_warning("WARNING: " + status_msg)
    else:
        print_ok1("SUCCESS: " + status_msg)

    print_header("END: Outbound Order Generation")
    return processed_orders, orders_batch
