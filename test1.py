

import pdfplumber

with pdfplumber.open("/Users/suresh/ggt-tasks/backups/requisitionReport-2956972-353806-20201210070110-68696.pdf") as pdf:
    is_reject_report = False
    reject_reason = ''
    first_page = pdf.pages[0]
    print(first_page.extract_text(x_tolerance=3, y_tolerance=3))
    for line in first_page.extract_text(x_tolerance=3, y_tolerance=3).splitlines():
        if line.startswith('Rejection Report'):
            is_reject_report=True
        if line.startswith('Comments:'):
            reject_reason = line.replace('Comments:','').strip()
    
    print(is_reject_report, reject_reason)

    


from twilio.rest import Client
sms_list = [['+19793133161999', '403597'],
            ['+19793133161999', '403541']]


def send_twilio_sms(to_number, message_text):
    account_sid = 'AC9cef9b4155030ee2683281ccc72d4001'
    auth_token = '62ee76165984c54f91ee80aac9cb3f0e'
    from_number = "+19723099019"

    try:
        client = Client(
            account_sid,
            auth_token
        )
        message = client.messages.create(
            to=to_number,
            from_=from_number,
            body=message_text
        )

        return True

    except Exception as err:
        print(err)
        return False


def __send_qrcode_sms(phone_number, appointment_id):
    message = "Click here for your Appointment Details\n {}/appointment/{}".format(
        'https://start.GoGetTested.com', str(appointment_id).rjust(6, '0'))

    print(message)
    # return send_twilio_sms(phone_number, message)


# for row in sms_list:
#  __send_qrcode_sms(row[0], row[1])


def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                     for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(response.error.message))

# export GOOGLE_APPLICATION_CREDENTIALS="./app/ggt/configs/gcp-service-account-prod.json"
#path = '/Users/suresh/ggt-tasks/insurance_images/463435_001.png'
# detect_text(path)


def hl7_test():
    from hl7apy.core import Message
    hl7 = Message("ORM_O01")
    hl7.msh.msh_3 = "SendingApp"
    hl7.msh.msh_4 = "SendingFac"
    hl7.msh.msh_5 = "ReceivingApp"
    hl7.msh.msh_6 = "ReceivingFac"
    hl7.msh.msh_9 = "ORM^O01^ORM_O01"
    hl7.msh.msh_10 = "168715"
    hl7.msh.msh_11 = "P"

    # PID
    hl7.add_group("ORM_O01_PATIENT")
    hl7.ORM_O01_PATIENT.pid.pid_2 = "475421"
    hl7.ORM_O01_PATIENT.pid.pid_3 = "A-10001"
    hl7.ORM_O01_PATIENT.pid.pid_5 = "B-10001"
    hl7.ORM_O01_PATIENT.pid.pid_6 = "DOE^JOHN"

    # ORC
    hl7.ORM_O01_ORDER.orc.orc_1 = "1"
    hl7.ORM_O01_ORDER.ORC.orc_10 = "20150414120000"


    # OBR
    # We must explicitly add the OBR segment, then populate fields

    #hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_OBSERVATION.ORM_O01_ORDER_CHOICE.add_segment("OBR")
    #hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_OBSERVATION.ORM_O01_ORDER_CHOICE.OBR.obr_2 = "1"
    #hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_OBSERVATION.ORM_O01_ORDER_CHOICE.OBR.obr_3 = "2"
    #hl7.ORM_O01_ORDER.ORM_O01_ORDER_DETAIL.ORM_O01_OBSERVATION.ORM_O01_ORDER_CHOICE.OBR.obr_4 = "1100"



    assert hl7.validate() is True

    print("\n Validate HL7 Message: ", hl7.validate())

    print("\n\n HL7 Message : \n\n", hl7.value)
    print("\n\n")

#hl7_test()


