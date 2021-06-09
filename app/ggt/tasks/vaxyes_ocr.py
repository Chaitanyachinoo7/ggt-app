from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

import ggt.lib.constants as c

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    replica_read_row,
    replica_read_rows
)

from ggt.models.data_models.data_types import (
    GgtThirdPartyGroup,
    GgtCustomField
)
from ggt.models.data_models.data_types import LookupGGVAddVaxCertRequest
from ggt.models.process_models.bp_patient_experience import __vax_card_pristine, __photo_id_pristine, __update_ocr_status

from ggt.lib.adapters.s3_adapter import get_temp_pkpass_url
def run_ocr_on_vax_yes_cards():
    print("starting run_ocr_on_vax_yes_cards job")
    unverified_certs = get_distinct_unverified_certs_patient_ids()
    # print(unverified_certs)
    final = 0
    for index, item in enumerate(unverified_certs):
        print(item)
        certs = get_unverified_certs(item["patient_id"])
        print(certs)
        if certs and len(certs):
            req = get_pristine_req(certs, str(item["patient_id"]))
            print(req.first_name)
            ocr = create_ocr_obj(item, certs)
            try:
                is_vax_card_pristine= __vax_card_pristine(str(item["patient_id"]), str(certs[0]["cert_id"]), req, ocr)
                is_photo_id_pristine = __photo_id_pristine(str(item["patient_id"]), str(certs[0]["cert_id"]), req, ocr)
                print(ocr)
                print("updating ocr db")
                __update_ocr_status(ocr["patient_id"], ocr["first_name"],ocr["last_name"],ocr["vax_type"],ocr["dob"],ocr["cert1_id"],ocr["first_vax_dt"],ocr["vax_1_lot_number"],
                ocr["cert2_id"],ocr["second_vax_dt"],ocr["vax_2_lot_number"])
                if is_vax_card_pristine and is_photo_id_pristine:
                    final = final + 1
            except Exception as err:
                log_generic(
                    type=c.ERROR,
                    function=whoami(),
                    error=err
                )
    print("L2 certs= "+ str(final))

def create_ocr_obj(item, certs):
    ocr = {
        "patient_id": None, 
        "first_name": 0, 
        "last_name": 0, 
        "vax_type": 0, 
        "dob": 0, 
        "cert1_id": None, 
        "first_vax_dt": 0, 
        "vax_1_lot_number": 0, 
        "cert2_id": None, 
        "second_vax_dt": 0, 
        "vax_2_lot_number": 0
    }
    ocr["patient_id"] = item["patient_id"]
    ocr["cert1_id"] = certs[0]["id"]
    if len(certs)>1:
        ocr["cert2_id"] = certs[1]["id"]
    print(ocr)
    return ocr

def get_pristine_req(certs, patient_id):
    vax_type = ""
    if "PFIZER" in certs[0]["service_code"]:
        vax_type = "pfizer"
    elif "MODERNA" in certs[0]["service_code"]:
        vax_type = "moderna"
    elif "JNJ" in certs[0]["service_code"]:
        vax_type = "janssen"
    req = lambda: None
    req.first_name = certs[0]["first_name"]
    req.last_name = certs[0]["last_name"]
    req.phone_number = certs[0]["phone_number"]
    req.email = certs[0]["email"]
    req.dob = certs[0]["dob"].strftime('%Y-%m-%d')
    req.vax_type = vax_type
    req.first_vax_dt = certs[0]["check_in_dt"].strftime('%Y-%m-%d')
    req.vax_1_lot_number = certs[0]["lot_no"]
    req.second_vax_dt = certs[1]["check_in_dt"].strftime('%Y-%m-%d') if len(certs)>1 else ""
    req.vax_2_lot_number = certs[1]["lot_no"] if len(certs)>1 else ""
    req.vax_image_url = get_temp_pkpass_url('{}/{}.jpg'.format(patient_id, str(certs[0]["cert_id"])), get_config_val('aws.vax_certificate_bucket'))
    return req
def get_distinct_unverified_certs_patient_ids():
    print("inside get_distinct_unverified_certs_patient_ids")
    sql = """
        SELECT distinct patient_id FROM ggv_certificates where create_dt > '2021-05-20' and verification_level < 2 order by id asc LIMIT 500
    """
    rows = read_rows(sql,)
    print(len(rows))
    return rows

def get_unverified_certs(patient_id):
    sql = """
        SELECT *, ggv_certificates.id as cert_id FROM ggv_certificates JOIN patients ON patients.id = ggv_certificates.patient_id where ggv_certificates.patient_id = %s
    """
    rows = read_rows(sql,(patient_id,))
    print(len(rows))
    return rows