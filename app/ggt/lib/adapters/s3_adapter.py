import boto3

from ggt.lib.utils import (
    get_config_val as cfg,
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


default_link_expiration_time_limit = cfg('aws.default_link_expiration_time_limit')
lab_reports_bucket_name = cfg('aws.lab_reports_bucket_name')

def __boto_connect_client(service):
    try:
        boto_client = boto3.client(
            service,
            aws_access_key_id=cfg('aws.access_key_id'),
            aws_secret_access_key=cfg('aws.secret_access_key'),
            region_name=cfg('aws.region')
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
            aws_access_key_id=cfg('aws.access_key_id'),
            aws_secret_access_key=cfg('aws.secret_access_key'),
            region_name=cfg('aws.region')
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
            aws_access_key_id=cfg('aws.access_key_id'),
            aws_secret_access_key=cfg('aws.secret_access_key'),
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


def move_file(source, destination, bucketName):
    try:
        print(source, destination)
        copy = __boto_connect_client('s3').copy_object(
            Bucket=bucketName, 
            CopySource=source, 
            Key=destination, 
            MetadataDirective="COPY"
        )
        delete = __boto_connect_client('s3').delete_object(
            Bucket=bucketName, 
            Key=source.replace(bucketName+"/", "")
        )
        return True

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return False


def get_temp_lab_report_url(filename: str):
    try:
        url = __boto_connect_client('s3').generate_presigned_url(
            'get_object',
            Params={
                'Bucket': lab_reports_bucket_name,
                'Key': filename
            },
            ExpiresIn=default_link_expiration_time_limit
        )
        return url

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None
