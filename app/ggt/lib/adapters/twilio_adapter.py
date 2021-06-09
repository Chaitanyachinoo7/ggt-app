from twilio.rest import Client

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)


from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)


def send_twilio_sms(to_number: str, message_text: str):
    account_sid = get_config_val('twilio.account_sid')
    auth_token = get_config_val('twilio.auth_token')
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

        log_generic(
            type=INFO,
            message_id=message.sid,
            to_number=to_number,
            message_text=message_text,
            function=whoami()
        )
        return True

    except Exception as err:
        log_generic(
            type=ERROR,
            to_number=to_number,
            message_text=message_text,
            function=whoami(),
            error=err
        )

    return False


def send_twilio_sms_short_code(to_number: str, message_text: str):
    if to_number[0:3] != "+52":
        account_sid = get_config_val('twilio.account_sid_short_code')
        auth_token = get_config_val('twilio.auth_token_short_code')
        from_number = get_config_val('twilio.from_number_short_code')
    else:
        account_sid = get_config_val('twilio.account_sid')
        auth_token = get_config_val('twilio.auth_token')
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

        log_generic(
            type=INFO,
            message_id=message.sid,
            to_number=to_number,
            message_text=message_text,
            function=whoami()
        )
        return True

    except Exception as err:
        log_generic(
            type=ERROR,
            to_number=to_number,
            message_text=message_text,
            function=whoami(),
            error=err
        )

    return False


def place_twilio_otp(to_number: str, otp: str, code_type: str):
    account_sid = get_config_val('twilio.account_sid_short_code')
    auth_token = get_config_val('twilio.auth_token_short_code')
    from_number = get_config_val('twilio.from_number_to_call')
    otp = ", ".join(otp)
    try:
        client = Client(
            account_sid,
            auth_token
        )
        execution = client.studio.flows('FW0d65754083307afba9ab60f83143943f').executions.create(to=to_number, 
        from_=from_number, parameters={"code_type": code_type, "otp": otp})

        log_generic(
            type = INFO,
            message_id = execution.sid,
            to_number = to_number,
            otp = otp,
            function = whoami()
        )
        return True

    except Exception as err:
        log_generic(
            type = ERROR,
            to_number = to_number,
            otp = otp,
            function = whoami(),
            error = err
        )
