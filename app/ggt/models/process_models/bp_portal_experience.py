from datetime import datetime
from cachetools import cached, LRUCache, TTLCache

import ggt.lib.constants as c
from ggt.lib.utils import (
    log_generic,
    whoami)
from ggt.models.data_models.clinical_test_results import (
    get_all_test_results,
    search_details_by_name_and_dob,
    get_test_details
)
from ggt.models.data_models.clinical_test_sample import (
    create_test_sample_from_appointment,
    record_label_scan,
    lab_status_update
)
from ggt.models.data_models.generic_search_result import (
    find_patients,
    find_patients_for_vaccineation
)
from ggt.models.data_models.groups import get_all_groups, create_group, update_group, get_group_by_id
from ggt.models.data_models.locations import (
    search_locations,
    create_location, update_location, assign_group, remove_group, assign_service, remove_service,
    get_all_locations_without_thumbnail, assign_all_groups, assign_all_services, remove_all_group, remove_all_service,
    get_states)
from ggt.models.data_models.service_catalog import get_all_services
from ggt.models.data_models.users import (
    get_user_by_email
)
import pdfrw
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import shutil
from ggt.lib.adapters.s3_adapter import uploadDirectory, create_folder

########################################################################################################
# [Public] functions
########################################################################################################


def bp_cc_search_details_by_name_and_dob(last_name, dob):
    return search_details_by_name_and_dob(last_name, dob)


def bp_cc_view_test_details(test_id):
    return get_test_details(test_id)


def bp_get_user_role(email):
    try:
        user = get_user_by_email(email)
        return user['role']

    except Exception as err:
        log_generic(
            type=c.ERROR,
            email=email,
            function=whoami(),
            error=err
        )


def bp_get_all_test_results():
    try:
        return get_all_test_results()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        # return False


#@cached(cache=TTLCache(maxsize=1024, ttl=60))
def bp_get_general_search_results(org_id, first_name, middle_name, last_name, dob, phone_number, email, appointment_id,
                                  group_code, appointment_date, location_id, vial_id='', sort_field="register_dt",
                                  sort_type="desc", group_vax_results=False, token=None, is_patient=False):
    try:
        if appointment_date != '':
            appointment_date = datetime.strptime(appointment_date, "%m%d%Y")

        search_results = find_patients(org_id, first_name, middle_name, last_name, dob, phone_number,
                             email, appointment_id, group_code, appointment_date, location_id, vial_id, sort_field,
                                       sort_type, token=token, is_patient=is_patient)
        if group_vax_results:
            return __group_vax_results(search_results)

        return search_results

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_get_f11(date):
    try:
        patients = find_patients_for_vaccineation(date)
        os.mkdir(date)
        os.mkdir(date+'/f11_overlay/')
        os.mkdir(date+'/consent_overlay/')
        os.mkdir(date+'/f11/')
        os.mkdir(date+'/consent/')
        # patient = patients[0]
        for patient in patients:
            if patient:
                data_dict = {}
                create_overlay(date, str(patient["id"]), patient, data_dict)
                create_overlay_consent_form(date, str(patient["id"]), patient)
                merge_pdfs('ggt/configs/vaccine-pdfs/F11-12956.pdf',
                        './'+date+'/f11_overlay/simple_form_overlay_' +
                        str(patient["id"])+'.pdf',
                        './'+date+'/f11/'+patient["last_name"].upper(
                        )+'_'+patient["first_name"].upper()+'_'+str(patient["dob"])+'_immtrac.pdf', data_dict)

                merge_pdfs('ggt/configs/vaccine-pdfs/COVID Concent Form.pdf',
                        './'+date+'/consent_overlay/consent_form_simple_form_overlay_' +
                        str(patient["id"])+'.pdf',
                        './'+date+'/consent/'+patient["last_name"].upper(
                        )+'_'+patient["first_name"].upper()+'_'+str(patient["dob"])+'_consent.pdf')
        shutil.rmtree(date+'/f11_overlay/')
        shutil.rmtree(date+'/consent_overlay/')
        create_folder("ggt-sftp", "brownwoodv/"+date)
        uploadDirectory(date, "ggt-sftp")
        shutil.rmtree(date)
        return True
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def create_overlay(date, patient_id, patient, data_dict, mother_first_name="", mother_maiden_name=""):
    c = canvas.Canvas(
        './'+date+'/f11_overlay/simple_form_overlay_'+patient_id+'.pdf')
    update_string_in_pdf(c, 25, 678, patient["last_name"].upper())
    update_string_in_pdf(c, 25, 646, patient["first_name"].upper())
    update_string_in_pdf(c, 320, 646, patient["middle_name"].upper())
    if patient["race"] == "American Indian or Alaska Native":
        update_string_in_pdf(c, 319, 698, "x")
        data_dict.update({'CheckBox1': 'Yes'})
    elif patient["race"] == "Asian":
        update_string_in_pdf(c, 319, 692, "x")
        data_dict.update({'CheckBox2': 'Yes'})
    elif patient["race"] == "Black or African American":
        update_string_in_pdf(c, 319, 688, "x")
        data_dict.update({'CheckBox3': 'Yes'})
    elif patient["race"] == "Native Hawaiian or Other Pacific Islander":
        update_string_in_pdf(c, 319, 682, "x")
        data_dict.update({'CheckBox4': 'Yes'})
    elif patient["race"] == "White":
        update_string_in_pdf(c, 319, 678, "x")
        data_dict.update({'CheckBox5': 'Yes'})
    elif patient["race"] == "Other":
        update_string_in_pdf(c, 319, 672, "x")
        data_dict.update({'CheckBox6': 'Yes'})
    if patient["ethnicity"] == "Hispanic or Latino":
        data_dict.update({'CheckBox7': 'Yes'})
    elif patient["ethnicity"] == "Not Hispanic or Latino":
        data_dict.update({'CheckBox8': 'Yes'})
    dob_splits = str(patient["dob"]).split('-')
    update_string_in_pdf(c, 25, 608, dob_splits[1])
    update_string_in_pdf(c, 68, 608, dob_splits[2])
    update_string_in_pdf(c, 105, 608, dob_splits[0])
    if patient["gender"] == "male":
        update_string_in_pdf(c, 492, 603, "X")
        data_dict.update({'Male': 'Yes'})
    elif patient["gender"] == "female":
        update_string_in_pdf(c, 541, 603, "X")
        data_dict.update({'Female': 'Yes'})
    update_string_in_pdf(c, 25, 577, patient["addr1"].upper())
    # update_string_in_pdf(c, 320, 602, "1234")
    phone = patient["phone_number"][2:]
    update_string_in_pdf(c, 420, 577, phone[:3]+"-"+phone[3:6]+"-"+phone[6:])
    update_string_in_pdf(c, 25, 545, patient["city"].upper())
    update_string_in_pdf(c, 315, 545, patient["st"])
    update_string_in_pdf(c, 360, 545, patient["zip"])
    update_string_in_pdf(c, 450, 545, "USA")
    # update_string_in_pdf(c, 25, 538, mother_first_name)
    # update_string_in_pdf(c, 320, 540, mother_maiden_name)
    c.drawString(
        55, 195, str(patient["scheduled_dt"]))
    c.drawString(
        300, 223, patient["first_name"].upper() + " " + patient["middle_name"].upper()+" " + patient["last_name"].upper())
    pdfmetrics.registerFont(
        TTFont('Allura-Regular', 'ggt/configs/vaccine-pdfs/Allura-Regular.ttf'))
    c.setFont("Allura-Regular", 15)
    c.drawString(
        300, 195, patient["first_name"] + " " + patient["middle_name"]+" " + patient["last_name"])
    c.save()


def create_overlay_consent_form(date, patient_id, patient, mother_first_name="", mother_maiden_name=""):
    c = canvas.Canvas(
        './'+date+'/consent_overlay/consent_form_simple_form_overlay_'+patient_id+'.pdf')
    c.drawString(50, 530, patient["last_name"].upper())
    c.drawString(205, 530, patient["first_name"].upper())
    c.drawString(350, 530, str(patient["dob"]))
    if patient["gender"] == "male":
        c.drawString(504, 530, "x")
    elif patient["gender"] == "female":
        c.drawString(504, 544, "x")
    c.drawString(50, 502, patient["addr1"].upper())
    phone = patient["phone_number"][2:]
    c.drawString(350, 502, phone[:3]+"-"+phone[3:6]+"-"+phone[6:])
    c.drawString(50, 465, patient["city"].upper())
    c.drawString(300, 465, patient["st"])
    c.drawString(350, 465, patient["zip"])
    c.showPage()
    c.drawString(
        200, 720, patient["first_name"].upper() + " " + patient["middle_name"].upper()+" " + patient["last_name"].upper())
    dob_splits = str(patient["dob"]).split('-')
    c.drawString(205, 702, dob_splits[1])
    c.drawString(245, 702, dob_splits[2])
    c.drawString(282, 702, dob_splits[0])
    c.save()


def update_string_in_pdf(c, x, y, entry):
    for char in entry:
        c.drawString(x, y, char)
        x = x + 14.3

ANNOT_KEY = '/Annots'           # key for all annotations within a page
ANNOT_FIELD_KEY = '/T'          # Name of field. i.e. given ID of field
ANNOT_FORM_type = '/FT'         # Form type (e.g. text/button)
ANNOT_FORM_button = '/Btn'      # ID for buttons, i.e. a checkbox
ANNOT_FORM_text = '/Tx'         # ID for textbox
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'
def merge_pdfs(form_pdf, overlay_pdf, output, data_dict=None):
    form = pdfrw.PdfReader(form_pdf)
    olay = pdfrw.PdfReader(overlay_pdf)

    for form_page, overlay_page in zip(form.pages, olay.pages):
        merge_obj = pdfrw.PageMerge()
        overlay = merge_obj.add(overlay_page)[0]
        pdfrw.PageMerge(form_page).add(overlay).render()

    writer = pdfrw.PdfWriter()
    if data_dict:
        # write_fillable_pdf(form, output, data_dict)
        # template_pdf = pdfrw.PdfReader(input_pdf_path)
        for Page in form.pages:
            if Page[ANNOT_KEY]:
                for annotation in Page[ANNOT_KEY]:
                    if annotation[ANNOT_FIELD_KEY] and annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                        # Remove parentheses
                        key = annotation[ANNOT_FIELD_KEY][1:-1]
                        if key in data_dict.keys():
                            if annotation[ANNOT_FORM_type] == ANNOT_FORM_button:
                                # button field i.e. a checkbox
                                annotation.update( pdfrw.PdfDict( V=pdfrw.PdfName(data_dict[key]) , AS=pdfrw.PdfName(data_dict[key]) ))
        form.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
    writer.write(output, form)



def bp_create_group(group):
    try:
        _id = create_group(group)
        if _id is None:
            return None
        return get_group_by_id(_id)
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_update_group(group):
    try:
        updated = update_group(group)
        if updated:
            return get_group_by_id(group.id)
        return None
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_create_location(location, org_id):
    try:
        l = create_location(location, org_id)
        if l is None:
            return None
        location_id = l['location_id']
        group_ids = location.group_ids
        service_ids = location.service_ids
        location_groups = []
        location_services = []

        for gid in group_ids:
            location_groups.append((gid, location_id))
        for sid in service_ids:
            location_services.append((location_id, sid))

        if len(location_groups) > 0:
            g_success = assign_all_groups(tuple(location_groups))
            if g_success is None or not g_success:
                return None
        if len(location_services) > 0:
            s_success = assign_all_services(tuple(location_services))
            if s_success is None or not s_success:
                return None
        _location = search_locations('', '', l['site_code'], '', org_id)
        return _location

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_assign_group(req):
    try:
        return assign_group(req)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_assign_service(req):
    try:
        return assign_service(req)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_remove_group(req):
    try:
        return remove_group(req)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_get_locations():
    try:
        return get_all_locations_without_thumbnail()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_remove_service(req):
    try:
        return remove_service(req)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_update_location(location, org_id):
    try:
        location_id = location.id
        update_location(location)
        remove_all_group(location_id)
        remove_all_service(location_id)
        group_ids = location.group_ids
        service_ids = location.service_ids
        location_groups = []
        location_services = []

        for gid in group_ids:
            location_groups.append((gid, location_id))
        for sid in service_ids:
            location_services.append((location_id, sid))

        if len(location_groups) > 0:
            g_success = assign_all_groups(tuple(location_groups))
            if g_success is None or not g_success:
                return None
        if len(location_services) > 0:
            s_success = assign_all_services(tuple(location_services))
            if s_success is None or not s_success:
                return None
        _location = search_locations('', '', '', '', org_id,  id=location_id)
        return _location

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_get_all_groups(user):
    try:
        return get_all_groups(user)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_get_states():
    try:
        return get_states()
    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_get_all_services():
    try:
        return get_all_services()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_get_location_search_results(account, group_code, site_code, location_name, st, org_id):
    try:
        return search_locations(account, group_code, site_code, location_name, org_id, st=st)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_create_test_sample_from_appointment(appointment_id):
    try:
        return create_test_sample_from_appointment(appointment_id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_record_label_scan(appointment_id):
    try:
        return record_label_scan(appointment_id)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def bp_lab_status_update(lab_status_update_request):
    try:
        return lab_status_update(lab_status_update_request)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )


def __group_vax_results(results):
    grouped_results = []
    vaccine_appointment_found = False
    grouped_vax_result = {
        "service": "COVID_19_VAX",
        "doses": []
    }

    for result in results:
        if result["service_code"] == c.SERVICE_CODE_COVID19_TEST:
            grouped_results.append(
                dict(result, service=c.SERVICE_CODE_COVID19_TEST))
        if result["service_code"] in [c.SERVICE_CODE_COVID_19_VACCINE_PFIZER_1,
                                      c.SERVICE_CODE_COVID_19_VACCINE_PFIZER_2,
                                      c.SERVICE_CODE_COVID_19_VACCINE_MODERNA_1,
                                      c.SERVICE_CODE_COVID_19_VACCINE_MODERNA_2]:
            grouped_vax_result["doses"].append(result)
            vaccine_appointment_found = True

    if vaccine_appointment_found:
        grouped_results.append(grouped_vax_result)

    return grouped_results
