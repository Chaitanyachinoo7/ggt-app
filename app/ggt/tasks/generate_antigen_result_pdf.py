import csv
import pathlib
from datetime import datetime
# ORGANIZATION_ID = 1
# SEASON_ID = 1
# PATH = pathlib.Path(__file__).parent.absolute()
from PIL import Image
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
import pathlib

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from dateutil.relativedelta import relativedelta

from ggt.lib.adapters.s3_adapter import put_to_bucket, read_file

from ggt.lib.adapters.mysql_adapter import exec_batch_execute, replica_read_rows, exec_update
from ggt.lib.utils import get_config_val

lab_report_bucket = get_config_val('lab_integrations.labreport_bucket')
current_dir = pathlib.Path(__file__).parent.absolute()

test_image_bucket = get_config_val("aws.ggt_ops_images")
antigen_test_result_bucket = 'ggt-test-bucket'


def generate_antigen_results_pdf():
    rows = get_all_appointment_information()
    processed_appointment_ids = generate_results_pdf(rows)
    update_test_samples(processed_appointment_ids)


def get_all_appointment_information():
    sql = """SELECT 
                    p.first_name,
                    p.last_name,
                    p.dob,
                    p.gender,
                    ts.test_result,
                    ts.sample_collection_end_dt,
                    ts.lab_electronic_submission_dt AS 'report_gen_dt',
                    ts.appointment_id,
                    ts.id
                FROM
                    test_samples ts
                        JOIN
                    appointment_services aps ON ts.appointment_id = aps.appointment_id
                        JOIN
                    services_catalog sc ON sc.id = aps.service_id
                        JOIN
                    patients p ON ts.patient_id = p.id
                WHERE
                    sc.service_code LIKE '%ANTIGEN%'
                        AND ts.status = 'with_lab';"""

    return replica_read_rows(sql)


def generate_results_pdf(rows):
    success_appointment_ids = []

    for row in rows:
        try:
            create_antigen_report_pdf(row)
            success_appointment_ids.append(row['appointment_id'])
        except Exception as e:
            print(e)

    return success_appointment_ids


def update_test_samples(processed_appointment_ids=[]):
    if len(processed_appointment_ids) < 2:
        processed_appointment_ids.append(0)

    sql = """UPDATE test_samples 
                    SET 
                        lab_result_receive_dt = NOW(),
                        status = 'lab_result_received'
                    WHERE id IN {}""".format(str(tuple(processed_appointment_ids)))
    return exec_update(sql)


def generate_patient_test_result_canvas(details):
    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)

    can.setFont("Helvetica-Bold", 10)

    can.drawString(425, 770, "Order: ")
    can.drawString(460, 770, str(details['appointment_id']))

    can.drawString(410, 760, "Patient ID: ")
    can.drawString(460, 760, str(details['id']))

    can.drawString(460, 720, "Check-Up")

    can.setFont("Helvetica", 10)

    can.drawString(30, 700, "Patient:")

    can.setFont("Helvetica-Bold", 10)

    can.drawString(75, 700, "{} {}".format(details['first_name'], details['last_name']))

    can.setFont("Helvetica", 10)

    can.drawString(30, 680, "Age:")

    can.setFont("Helvetica-Bold", 10)

    can.drawString(60, 680, "{} years".format(relativedelta(datetime.now(), details['dob']).years))

    can.setFont("Helvetica", 10)

    can.drawString(110, 680, "Sex:")

    can.setFont("Helvetica-Bold", 10)

    gender = details['gender'][0:1].upper()
    can.drawString(130, 680, gender)

    can.setFont("Helvetica", 10)

    can.drawString(30, 660, "Date: ")

    can.setFont("Helvetica-Bold", 10)

    sample_collection_dt = details['sample_collection_end_dt']
    can.drawString(60, 660, sample_collection_dt.strftime("%d/%m/%y %z"))

    can.setFont("Helvetica", 10)

    can.drawString(30, 640, "Address to: ")

    can.setFont("Helvetica-Bold", 10)

    can.drawString(95, 640, "Dr. (to whom it may concern)")

    can.setFont("Helvetica", 10)

    can.drawString(60, 600, "This is the report of the study you have requested from your patient.")

    can.setFont("Helvetica-Bold", 10)

    can.drawString(60, 570, "SARS-CoV-2 (COVID-19) Antigen Test")

    can.drawString(60, 530, "Result")

    is_result_positive = details['test_result'] == 'pos'
    displayed_result = '__POSITIVE__' if is_result_positive else "___NEGATIVE___"

    can.drawString(60, 495, displayed_result)

    can.setFont("Helvetica", 10)

    can.drawString(130, 465, "Sample collection: ")

    sample_collection_dt = details['sample_collection_end_dt']
    can.drawString(220, 465, sample_collection_dt.strftime("%H:%Mh"))

    can.drawString(175, 435, "Report: ")
    report_gent_dt = details['report_gen_dt']
    can.drawString(220, 435, report_gent_dt.strftime("%H:%Mh"))

    can.drawString(70, 405, "Sample processing technician: ")
    can.drawString(220, 405, "")

    can.setFont("Helvetica-Bold", 10)

    can.drawString(60, 360, "Method: Immunoassay")

    can.drawString(60, 230, "*** FINAL REPORT ***")

    can.setFont("Helvetica", 10)

    can.drawString(60, 190, "Sincerely,")

    can.setFont("Helvetica-Bold", 10)

    can.drawString(60, 170, "Dr. Alejandro Estanes Hernández")

    can.setFont("Helvetica", 10)

    can.drawString(60, 150, "Professional license 2649517")

    can.drawString(60, 130, "Universidad Nacional Autónoma de México UNAM")
    can.drawString(60, 110, "RVC-D103208-1-35-042")

    can.save()

    return packet


def generate_patients_test_result_page(details):
    # Get the canvas object
    packet = generate_patient_test_result_canvas(details)

    # move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)

    return new_pdf


def generate_patient_test_image_canvas(image):
    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)

    can.drawImage(image, 150, 400, 100, 100)
    can.save()
    return packet


def generate_patient_test_result_image_page(details):
    try:
        image_name = 'test_result_images/{}.png'.format(details['appointment_id'])
        img_bytes = read_file(test_image_bucket, image_name)
        if not img_bytes:
            return None
        # Generate image from the byte
        img = Image.open(io.BytesIO(img_bytes))
        packet = generate_patient_test_image_canvas(ImageReader(img))

        # move to the beginning of the StringIO buffer
        packet.seek(0)
        new_pdf = PdfFileReader(packet)

        return new_pdf

    except Exception as err:
        print(err)
        return None


def create_antigen_report_pdf(details):

    # read your existing PDF
    existing_pdf = PdfFileReader(open(current_dir.joinpath("../templates/pdf/antigen-report-no-text.pdf"), "rb"))

    pdf_with_test_result = generate_patients_test_result_page(details)
    pdf_with_test_image = generate_patient_test_result_image_page(details)
    output = PdfFileWriter()

    # First page will have patient details
    page = existing_pdf.getPage(0)
    page.mergePage(pdf_with_test_result.getPage(0))
    output.addPage(page)

    # If there is an image pdf, append it to the second page
    if pdf_with_test_image:
        empty_page = existing_pdf.getPage(1)
        empty_page.mergePage(pdf_with_test_image.getPage(0))
        output.addPage(empty_page)

    # Create in memory byte stream to get the content of the pdf
    byte_stream = io.BytesIO()
    output.write(byte_stream)

    # S3 file name
    file_name = "{} {} {} report.pdf".format(details['first_name'], details['last_name'], details['appointment_id'])

    # Push to S3
    put_to_bucket(antigen_test_result_bucket, byte_stream.getvalue(), 'application/pdf', file_name)
