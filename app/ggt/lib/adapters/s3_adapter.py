import os
import boto3
from botocore.client import Config

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


default_link_expiration_time_limit = cfg(
    'aws.default_link_expiration_time_limit')
lab_reports_bucket_name = cfg('aws.lab_reports_bucket_name')


def __boto_connect_client(service, region_name='us-east-2'):
    try:
        if service == 's3':
            boto_client = boto3.client(
                's3',
                aws_access_key_id=cfg('aws.access_key_id'),
                aws_secret_access_key=cfg('aws.secret_access_key'),
                config=Config(signature_version='s3v4'),
                region_name=region_name
            )
        else:
            boto_client = boto3.client(
                service,
                aws_access_key_id=cfg('aws.access_key_id'),
                aws_secret_access_key=cfg('aws.secret_access_key'),
                region_name=region_name
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
        response = __boto_connect_client('s3').put_object(
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
            bucket_name=bucket_name,
            directory_name=directory_name,
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


def get_temp_lab_report_url(filename: str, lab_reports_bucket_name=lab_reports_bucket_name):
    try:
        url = __boto_connect_client('s3').generate_presigned_url(
            ClientMethod='get_object',
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


def iterate_bucket_items(bucket):
    """
    Generator that iterates over all objects in a given s3 bucket

    See http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.list_objects_v2 
    for return data format
    :param bucket: name of s3 bucket
    :return: dict of metadata for an object
    """

    client = __boto_connect_client('s3')
    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket)

    for page in page_iterator:
        if page['KeyCount'] > 0:
            for item in page['Contents']:
                yield item


def uploadDirectory(path, bucketName):
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                __boto_connect_client('s3').upload_file(os.path.join(
                    root, file), bucketName, "brownwoodv/"+path+'/'+file)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None

def get_temp_vaccine_consent_url(filename: str, lab_reports_bucket_name=lab_reports_bucket_name):
    try:
        url = __boto_connect_client('s3','us-east-1').generate_presigned_url(
            ClientMethod='get_object',
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
