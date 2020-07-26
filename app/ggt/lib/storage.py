from ggt.lib.adapters.google_adapter import (
    upload_lab_report as __upload_lab_report,
    upload_insurance_card as __upload_insurance_card,
    get_temp_lab_report_url as __get_temp_lab_report_url,
    get_temp_insurance_card_url as __get_temp_insurance_card_url
)


def upload_lab_report(local_file_path, destination_file_name):
    return __upload_lab_report(local_file_path, destination_file_name)

def upload_insurance_card_file(local_file_path, destination_file_name):
    return __upload_insurance_card(local_file_path, destination_file_name)

def get_temporary_lab_report_url(file_name):
    return __get_temp_lab_report_url(file_name)

def get_temporary_insurance_card_url(file_name):
    return __get_temp_insurance_card_url(file_name)

###TODO:
###def upload_insurance_card_base64_string():
