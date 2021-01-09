from ggt.lib.adapters.twilio_adapter import send_twilio_sms, send_twilio_sms_short_code
from ggt.lib.adapters.sns_adapter import send_sns_sms
from ggt.lib.adapters.pinpoint_adapter import send_pinpoint_message


def send_sms(to_number, message, priority=2):
    if priority == 1:
        return send_twilio_sms_short_code(to_number, message)
    elif priority == 9:
        return send_pinpoint_message(to_number, message)
    return send_twilio_sms(to_number, message)
    # return send_sns_sms(to_number, message)
    # pass

# return send_sns_sms(to_number, message)
