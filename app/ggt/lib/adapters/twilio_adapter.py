from twilio.rest import Client

from ggt.lib.utils import (
    get_config_val,
    log_generic
)




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

        log_generic(type="info", message_id=message.sid, to_number=to_number, message_text=message_text, function='send_twilio_sms', info='SMS Sent')
        return True

    except Exception as err:
        log_generic(type="error", to_number=to_number, message_text=message_text, function='send_twilio_sms', error=err)
        return False


