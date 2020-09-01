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



for row in sms_list:
  __send_qrcode_sms(row[0], row[1])

