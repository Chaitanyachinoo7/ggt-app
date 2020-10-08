import boto3

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


def __boto_connect():
    try:
        boto_client = boto3.client(
            "sns",
            aws_access_key_id=get_config_val('aws.access_key_id'),
            aws_secret_access_key=get_config_val('aws.secret_access_key'),
            region_name=get_config_val('aws.region')
        )
        return boto_client

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def send_sns_sms(to_number, message):
    try:
        response = __boto_connect().publish(
            PhoneNumber=to_number,
            Message=message
        )
        log_generic(
            type=INFO,
            message_id=response['MessageId'],
            to_number=to_number,
            message=message,
            function=whoami()
        )
        return True

    except Exception as err:
        log_generic(
            type=ERROR,
            to_number=to_number,
            message=message,
            function=whoami(),
            error=err
        )
        return False
