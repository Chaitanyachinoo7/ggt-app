from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

import pathlib
current_dir = pathlib.Path(__file__).parent.absolute()


def generate_canvas():
    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)

    can.setFont("Helvetica-Bold", 10)

    can.drawString(425, 770, "Order: ")
    can.drawString(460, 770, "PZ00009501")

    can.drawString(410, 760, "Patient ID: ")
    can.drawString(460, 760, "16048603")

    can.drawString(460, 720, "Check-Up")

    can.setFont("Helvetica", 10)

    can.drawString(30, 700, "Patient:")

    can.setFont("Helvetica-Bold", 10)

    can.drawString(75, 700, "Juan Igelius")

    can.setFont("Helvetica", 10)

    can.drawString(30, 680, "Age:")

    can.setFont("Helvetica-Bold", 10)

    can.drawString(60, 680, "48 years")

    can.setFont("Helvetica", 10)

    can.drawString(90, 680, "Sex:")

    can.setFont("Helvetica-Bold", 10)

    can.drawString(120, 680, "M")

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

    can.drawString(60, 495, "___NEGATIVE___")

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


def create_antigen_report_pdf():

    packet = generate_canvas()

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
    output_stream = open("destination.pdf", "wb")
    output.write(output_stream)
    output_stream.close()

