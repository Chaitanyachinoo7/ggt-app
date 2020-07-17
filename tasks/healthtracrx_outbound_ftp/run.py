from ..app.ggt.lib.utils import (
    get_config_val,
    generate_otp,
    generate_token,
    validate_phone_number_format,
    log_generic
)

from ..app.ggt.lib.mysql_adapter import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows
)

sql = """
INSERT INTO `ggt`.`healthtracrx_transmissions`
(`test_id`,
`patient_id`,
`first_name`,
`last_name`,
`dob`,
`gender`,
`race`,
`ethnicity`,
`addr1`,
`addr2`,
`city`,
`st`,
`zip`,
`phone`,
`client_site_code`,
`physician_npi`,
`bill`,
`client_order_number`,
`sample_type`,
`sample_source`,
`date_of_collection`,
`panel_code`,
`panel_name`)
SELECT * FROM ggt.tests_ready_to_tx_view;
"""

sql = """
SELECT 
    patient_id,
    first_name,
    last_name,
    dob,
    gender,
    race,
    ethnicity,
    addr1,
    addr2,
    city,
    st,
    zip,
    phone_number,
    client_site_code,
    physician_npi,
    bill,
    client_order_number,
    sample_type,
    sample_source,
    date_of_collection,
    panel_code,
    panel_name
FROM
    tests_ready_to_tx_view
"""

print('hi')