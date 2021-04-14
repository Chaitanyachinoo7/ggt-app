import base64
import os
import boto3
from botocore.client import Config
import requests
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
ops_image_bucket_name = cfg('aws.ggt_ops_images')


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


def __boto_connect_resource(service, region_name='us-east-2'):
    try:
        if service == 's3':
            boto_client = boto3.resource(
                's3',
                aws_access_key_id=cfg('aws.access_key_id'),
                aws_secret_access_key=cfg('aws.secret_access_key'),
                config=Config(signature_version='s3v4'),
                region_name=region_name
            )
        else:
            boto_client = boto3.resource(
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
            Key=(directory_name + '/')
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


def move_file(source_bucket, source_key, dest_bucket, dest_key):
    try:
        if copy_file_from_s3_to_s3(source_bucket, source_key, dest_bucket, dest_key):
            s3 = __boto_connect_resource('s3')
            s3.Object(source_bucket, source_key).delete()
            return True

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )

    return False


def delete_file(source_bucket, source_key):
    try:
        s3 = __boto_connect_resource('s3')
        if s3.Object(source_bucket, source_key).delete():
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


def get_list_of_files(bucket_name, prefix):
    s3 = __boto_connect_resource('s3')
    bucket = s3.Bucket(bucket_name)
    files = []

    for file in bucket.objects.filter(
        Prefix=prefix
    ):
        files.append(file.key)

    return files


def get_file_iterator(bucket, prefix='', suffix='', get_last_modified=False):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    s3 = boto3.client('s3')
    kwargs = {'Bucket': bucket}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix

    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3.list_objects_v2(**kwargs)
        if resp['KeyCount'] == 0:
            return []
        for obj in resp['Contents']:
            key = obj['Key']
            last_modified = obj['LastModified']
            if key.startswith(prefix) and key.endswith(suffix):
                if get_last_modified:
                    yield key, last_modified
                else:
                    yield key

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break


def copy_file_from_s3_to_s3(source_bucket, source_key, dest_bucket, dest_key):
    try:
        s3 = __boto_connect_resource('s3')

        copy_source = {
            'Bucket': source_bucket,
            'Key': source_key
        }

        bucket = s3.Bucket(dest_bucket)
        bucket.copy(copy_source, dest_key)
        return True

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            operation='{}/{} ==> {}/{}'.format(source_bucket,
                                               source_key, dest_bucket, dest_key),
            error=err
        )

    return False


def file_exists(bucket, filename):
    try:
        if __boto_connect_client('s3').head_object(Bucket=bucket, Key=filename).get('ResponseMetadata', None) is None:
            return False
        else:
            return True

    except Exception:
        return False


def read_file(bucket, filename):
    try:
        s3 = __boto_connect_resource('s3')
        obj = s3.Object(bucket, filename)
        body = obj.get()['Body'].read()
        return body

    except Exception:
        return None


def uploadDirectory(path, bucketName):
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                __boto_connect_client('s3').upload_file(os.path.join(
                    root, file), bucketName, "brownwoodv/" + path + '/' + file)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_temp_vaccine_consent_url(filename: str, lab_reports_bucket_name=lab_reports_bucket_name):
    try:
        url = __boto_connect_client('s3', 'us-east-1').generate_presigned_url(
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


def get_temp_pkpass_url(filename, bucket_name):
    try:
        url = __boto_connect_client('s3', region_name='us-east-2').generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
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


def upload_image_from_base64_string(base64string, destination_filename, bucket_name, key=None):
    if key:
        destination_filename = "{}/{}".format(key, destination_filename)

    if bucket_name is None:
        bucket_name = ops_image_bucket_name
    try:
        s3 = __boto_connect_resource('s3')
        obj = s3.Object(bucket_name, destination_filename)
        return obj.put(Body=base64.b64decode(base64string))
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def upload_image_from_twilio(url, file_name, bucket_name=None):
    print(url)
    r = requests.get(url, stream=True)

    if bucket_name is None:
        bucket_name = ops_image_bucket_name
    session = boto3.Session()
    s3 = __boto_connect_resource('s3')
    bucket = s3.Bucket(bucket_name)
    try:
        bucket.upload_fileobj(r.raw, file_name)
        return True
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def uploadFile(path, key, bucketName):
    try:
        __boto_connect_client('s3').upload_file(path, bucketName, key)
    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None
