sms_list = [['+19793133161999','403597'],
['+19793133161999','403541']]



from twilio.rest import Client



def send_twilio_sms(to_number, message_text):
    account_sid = 'AC9cef9b4155030ee2683281ccc72d4001'
    auth_token  = '62ee76165984c54f91ee80aac9cb3f0e'
    from_number =  "+19723099019"
    
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
    #return send_twilio_sms(phone_number, message)



#for row in sms_list:
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

###export GOOGLE_APPLICATION_CREDENTIALS="./app/ggt/configs/gcp-service-account-prod.json"
path = '/Users/suresh/ggt-tasks/insurance_images/463435_001.png'
detect_text(path)