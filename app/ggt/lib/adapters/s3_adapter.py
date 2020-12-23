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


def __boto_connect_client(service):
    try:
        boto_client = boto3.client(
            service,
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


def __boto_connect_session():
    try:
        boto_session = boto3.Session(
            aws_access_key_id=get_config_val('aws.access_key_id'),
            aws_secret_access_key=get_config_val('aws.secret_access_key'),
            region_name=get_config_val('aws.region')
        )
        return boto_session

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def __boto_connect_resource(service, region_name='us-east-1'):
    try:
        boto_resource = boto3.resource(
            service_name=service,
            region_name=region_name,
            aws_access_key_id=get_config_val('aws.access_key_id'),
            aws_secret_access_key=get_config_val('aws.secret_access_key'),
        )
        return boto_resource

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def create_folder(bucket_name, directory_name):
    try:
        response = __boto_connect_service('s3').put_object(
            Bucket=bucket_name,
            Key=(directory_name+'/')
        )
        log_generic(
            type=INFO,
            bucket_name=bucket_name,
            directory_name=directory_name,
            function=whoami()
        )
        return True

    except Exception as err:
        log_generic(
            type=ERROR,
            queue_url=queue_url,
            message=message,
            function=whoami(),
            error=err
        )
        return False



def write_text_file(bucket, filename, body):
    try:
        if __boto_connect_client('s3').put_object(Body=body, Bucket=bucket, Key=filename):
            return True

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
    
    return False




