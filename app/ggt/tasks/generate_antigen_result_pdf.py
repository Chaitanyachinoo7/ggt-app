import csv
import pathlib
from datetime import datetime
# ORGANIZATION_ID = 1
# SEASON_ID = 1
# PATH = pathlib.Path(__file__).parent.absolute()

from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from dateutil.relativedelta import relativedelta

from ggt.lib.adapters.s3_adapter import put_to_bucket

import pathlib
current_dir = pathlib.Path(__file__).parent.absolute()

from ggt.lib.adapters.mysql_adapter import exec_batch_execute, replica_read_rows, exec_update
from ggt.lib.utils import get_config_val

lab_report_bucket = get_config_val('lab_integrations.labreport_bucket')


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


def generate_canvas(details):
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

    can.drawString(60, 660, "21/05/2021 (GMT-6)")

    can.setFont("Helvetica", 10)

    can.drawString(30, 640, "Address to: ")

    can.setFont("Helvetica-Bold", 10)

    can.drawString(95, 640, "Dr. (to whom it may concern)")

    can.setFont("Helvetica", 10)

    can.drawString(60, 600, "This is the report of the study you have requested from your patient.")

    can.setFont("Helvetica-Bold", 10)

    can.drawString(60, 570, "SARS-CoV-2 (COVID-19) Antigen Test")

    can.drawString(60, 530, "Result")

    is_result_postive = details['test_result'] == 'pos'
    displayed_result = '__POSITIVE__' if is_result_postive else "___NEGATIVE___"

    can.drawString(60, 495, displayed_result)

    can.setFont("Helvetica", 10)

    can.drawString(130, 465, "Sample collection: ")
    can.drawString(220, 465, "12:32h (GMT-6))")

    can.drawString(175, 435, "Report: ")
    can.drawString(220, 435, "12:47h (GMT-6))")

    can.drawString(70, 405, "Sample processing technician: ")
    can.drawString(220, 405, "7946")

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


def create_antigen_report_pdf(details):

    packet = generate_canvas(details)

    # move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(open(current_dir.joinpath("../templates/pdf/antigen-report-no-text.pdf"), "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    # output_stream = open("destination.pdf", "wb")
    # output.write(output_stream)
    # output_stream.close()
    byte_stream = io.BytesIO()
    output.write(byte_stream)

    file_name = "{} {} report".format(details['first_name'], details['last_name'])

    put_to_bucket('ggt-test-bucket', byte_stream.getvalue(), 'application/pdf', file_name)



