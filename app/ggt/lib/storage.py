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
    get_list_of_all_uploaded_inbound_files as __get_list_of_all_uploaded_inbound_files,
    get_file_blob as __get_file_blob,
    upload_archived_notification_from_base64_string as __upload_archived_notification_from_base64_string
)


async def upload_to_all_inbound_files(local_file_path, destination_filename):
    return await __upload_to_all_inbound_files(local_file_path, destination_filename)


async def file_exists_in_all_inbound_files(filename):
    return await __file_exists_in_all_inbound_files(filename)


async def file_exists_in_lab_reports(filename):
    return await __file_exists_in_lab_reports(filename)


async def file_exists_in_insurance_cards(filename):
    return await __file_exists_in_insurance_cards(filename)


async def upload_lab_report(local_file_path, destination_filename):
    return await __upload_lab_report(local_file_path, destination_filename)


async def upload_insurance_card_file(local_file_path, destination_filename):
    return await __upload_insurance_card(local_file_path, destination_filename)


async def upload_insurance_card_from_base64_string(base64string, content_type, destination_filename):
    return await __upload_insurance_card_from_base64_string(base64string, content_type, destination_filename)


async def get_temporary_lab_report_url(filename):
    return await __get_temp_lab_report_url(filename)


async def get_temporary_insurance_card_url(filename):
    return await __get_temp_insurance_card_url(filename)
    

async def get_list_of_all_uploaded_lab_reports():
    return await __get_list_of_all_uploaded_lab_reports


async def get_list_of_all_uploaded_inbound_files():
    return await __get_list_of_all_uploaded_inbound_files


async def get_file_blob(bucket_name, filename):
    return await __get_file_blob(bucket_name, filename)

async def upload_archived_notification_from_base64_string(bucket_name: str, base64string: str, content_type: str, destination_blob_name: str) -> bool:
    return await __upload_archived_notification_from_base64_string(bucket_name, base64string, content_type, destination_blob_name)
