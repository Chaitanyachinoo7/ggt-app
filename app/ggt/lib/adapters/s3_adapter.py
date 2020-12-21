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
            "s3",
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

    


def create_folder(bucket_name, directory_name):
    try:
        response = __boto_connect().put_object(
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
            type = ERROR,
            queue_url = queue_url,
            message = message,
            function = whoami(),
            error = err
        )
        return False

def move_file(source_file, destination_file):
    try:
        s3_client = __boto_connect()
        s3_client.object()

        response = __boto_connect().put_object(
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
            type = ERROR,
            queue_url = queue_url,
            message = message,
            function = whoami(),
            error = err
        )
        return False



    s3_resource = boto3.resource(‘s3’)
# Copy object A as object B
s3_resource.Object(“bucket_name”, “newpath/to/object_B.txt”).copy_from(
 CopySource=”path/to/your/object_A.txt”)
# Delete the former object A
s3_resource.Object(“bucket_name”, “path/to/your/object_A.txt”).delete()
