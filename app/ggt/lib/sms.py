from ggt.lib.adapters.twilio_adapter import send_twilio_sms
from ggt.lib.adapters.sns_adapter import send_sns_sms


def send_sms(to_number, message):
    return send_twilio_sms(to_number, message)


#return send_sns_sms(to_number, message)
