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
        boto_resource = boto3.resource(
            "dynamodb",
            aws_access_key_id=get_config_val('aws.access_key_id'),
            aws_secret_access_key=get_config_val('aws.secret_access_key'),
            region_name=get_config_val('aws.region')
        )

        return boto_resource

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def read_from_dynamo(table, message_id):
    try:
        table = __boto_connect().Table(table)
        return table.get_item(
            Key={
                'message_id': message_id
            }
        )
        log_generic(
            type=INFO,
            table=table,
            message_id=message_id,
            function=whoami()
        )

    except Exception as err:
        log_generic(
            type=ERROR,
            table=table,
            message_id=message_id,
            function=whoami(),
            error=err
        )
        return False
