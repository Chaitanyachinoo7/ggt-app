import boto3

from ggt.lib.utils import (
    get_config_val,
    log_generic
)


def __boto_connect():
    try:
        boto_client = boto3.client(
            "sqs",
            aws_access_key_id = get_config_val('aws.access_key_id'),
            aws_secret_access_key = get_config_val('aws.secret_access_key'), 
            region_name = get_config_val('aws.region')
        )
        return boto_client

    except Exception as err:
        log_generic(type="error", function='__boto_connect', error=err)
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
        log_generic(type="info", queue_url=queue_url, message=message, function='push_sqs_message', message_id=response['MessageId'])
        return True

    except Exception as err:
        log_generic(type="error", queue_url=queue_url, message=message, function='push_sqs_message', error=err)
        return False
