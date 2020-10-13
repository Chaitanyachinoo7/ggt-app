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
            "sqs",
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


def push_sqs_message(queue_url, message):
    try:
        response = __boto_connect().send_message(
                        QueueUrl=queue_url,
                        DelaySeconds=10,
                        MessageBody=(
                            {
                                "test": "test"
                            }
                        )
                    )
        log_generic(
            type=INFO,
            queue_url=queue_url,
            message=message,
            function=whoami()
        )
        return True

    except Exception as err:
        log_generic(
            type = ERROR,
            queue_url = queue_url,
            message = message,
            function = whoami(),
            error = err
        )
        return False
