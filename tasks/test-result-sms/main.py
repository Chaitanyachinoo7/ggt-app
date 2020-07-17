from pathlib import Path
'''

from .app.ggt.lib.utils import (
    get_config_val,
    log_generic
)
log_config_file = curr_file.parent.joinpath("log-config.yml")
config_file = curr_file.parent.joinpath("config.yml")


from twilio.rest import Client








def send_twilio_sms(to_number, message_text):
    account_sid = get_config_val('twilio.account_sid')
    auth_token  = get_config_val('twilio.auth_token')
    from_number = get_config_val('twilio.from_number')
    
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

        log_info(log_detail="message-id: {}".format(message.sid))
        return True

    except Exception as err:
        return False

'''




from twilio.rest import Client



def send_twilio_sms(to_number, message_text):
    account_sid = "AC9cef9b4155030ee2683281ccc72d4001"
    auth_token  = "62ee76165984c54f91ee80aac9cb3f0e"
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

        print("message-id: {}".format(message.sid))
        return True

    except Exception as err:
        print("sending-sms-failed: {}".format(err))
        print("from: {} / to: {} / message: {}".format(from_number, to_number, message_text))
        return False



def test():
    '''
    10/01/2000
    08/24/1993
    07/03/2002
    '''
    import io
    import csv

    with open('result-test.csv', newline = '') as results_data:                                                                                          
    	results_data_reader = csv.reader(results_data, delimiter='\t')
    	for result in results_data_reader:
            first_name = result[1]
            token = result[0]
            phone = result[3]
            message = "Hi {}, your GoGetTested.com COVID-19 test results are available. Please follow this link to view your results https://start-dev.gogettested.com/r/{}".format(first_name, token)

            send_twilio_sms(phone, message)

    
def send_production_list():
    import io
    import csv

    with open('result.07.15.2020.csv', newline = '') as results_data:                                                                                          
    	results_data_reader = csv.reader(results_data, delimiter='\t')
    	for result in results_data_reader:
            first_name = result[1]
            token = result[0]
            phone = result[3]
            message = "Hi {}, your GoGetTested.com COVID-19 test results are available. Please follow this link to view your results https://start.gogettested.com/r/{}".format(first_name, token)

            send_twilio_sms(phone, message)


if __name__ == '__main__':
    send_production_list()
