from ggt.lib.adapters.google_adapter import (
    file_exists_in_all_inbound_files as __file_exists_in_all_inbound_files,
    file_exists_in_lab_reports as __file_exists_in_lab_reports,
    file_exists_in_insurance_cards as __file_exists_in_insurance_cards,
    upload_lab_report as __upload_lab_report,
    upload_insurance_card as __upload_insurance_card,
    upload_insurance_card_from_base64_string as __upload_insurance_card_from_base64_string,
    upload_to_all_inbound_files as __upload_to_all_inbound_files,
    get_temp_lab_report_url as __get_temp_lab_report_url,
    get_temp_insurance_card_url as __get_temp_insurance_card_url,
    get_list_of_all_uploaded_lab_reports as __get_list_of_all_uploaded_lab_reports,
    get_list_of_all_uploaded_inbound_files as __get_list_of_all_uploaded_inbound_files
)


def upload_to_all_inbound_files(local_file_path, destination_filename):
    return __upload_to_all_inbound_files(local_file_path, destination_filename)


def file_exists_in_all_inbound_files(filename):
    return __file_exists_in_all_inbound_files(filename)


def file_exists_in_lab_reports(filename):
    return __file_exists_in_lab_reports(filename)


def file_exists_in_insurance_cards(filename):
    return __file_exists_in_insurance_cards(filename)


def upload_lab_report(local_file_path, destination_filename):
    return __upload_lab_report(local_file_path, destination_filename)


def upload_insurance_card_file(local_file_path, destination_filename):
    return __upload_insurance_card(local_file_path, destination_filename)


def upload_insurance_card_from_base64_string(base64string, content_type, destination_filename):
    return __upload_insurance_card_from_base64_string(base64string, content_type, destination_filename)


def get_temporary_lab_report_url(filename):
    return __get_temp_lab_report_url(filename)


def get_temporary_insurance_card_url(filename):
    return __get_temp_insurance_card_url(filename)
    

def get_list_of_all_uploaded_lab_reports():
    return __get_list_of_all_uploaded_lab_reports


def get_list_of_all_uploaded_inbound_files():
    return __get_list_of_all_uploaded_inbound_files
