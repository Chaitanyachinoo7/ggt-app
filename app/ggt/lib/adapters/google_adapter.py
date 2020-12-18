import datetime
import collections
import hashlib
import binascii
import base64
from pathlib import Path
import six
from six.moves.urllib.parse import quote

from google.cloud import storage
from google.oauth2 import service_account

from ggt.lib.utils import (
    get_config_val as cfg,
    log_generic,
    whoami
)

import ggt.lib.constants as c


curr_file = Path(__file__)

service_account_file = cfg('gcp.service_account_file')
service_account_file_prod = cfg('gcp.service_account_file_prod')
service_account_file = curr_file.parent.parent.parent.joinpath(
    'configs/{}'.format(service_account_file))
service_account_file_prod = curr_file.parent.parent.parent.joinpath(
    'configs/{}'.format(service_account_file_prod))

default_link_expiration_time_limit = cfg(
    'gcp.default_link_expiration_time_limit')
lab_reports_bucket_name = cfg('gcp.lab_reports_bucket_name')
insurance_cards_bucket_name = cfg('gcp.insurance_cards_bucket_name')
all_inbound_files_bucket_name = cfg(
    'gcp.all_inbound_files_bucket_name')


def upload_lab_report(local_file_path: str, destination_filename: str) -> bool:
    try:
        return upload_blob(
            lab_reports_bucket_name,
            local_file_path,
            destination_filename
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return False


def get_list_of_all_uploaded_lab_reports():
    try:
        return get_file_list_in_bucket(lab_reports_bucket_name)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_list_of_all_uploaded_inbound_files():
    try:
        return get_file_list_in_bucket(all_inbound_files_bucket_name)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def upload_insurance_card(local_file_path: str, destination_filename: str) -> bool:
    try:
        return upload_blob(
            insurance_cards_bucket_name,
            local_file_path,
            destination_filename
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return False


def upload_insurance_card_from_base64_string(base64string: str, content_type: str, destination_blob_name: str) -> bool:
    try:
        return upload_blob_from_string(
            insurance_cards_bucket_name,
            base64string,
            content_type,
            destination_blob_name
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return False


def upload_archived_notification_from_base64_string(bucket_name: str, base64string: str, content_type: str, destination_blob_name: str) -> bool:
    try:
        return upload_blob_from_string(
            bucket_name,
            base64string,
            content_type,
            destination_blob_name
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return False


def get_temp_lab_report_url(filename: str):
    try:
        return get_signed_url(
            lab_reports_bucket_name,
            filename
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_temp_insurance_card_url(filename: str):
    try:
        return get_signed_url(
            insurance_cards_bucket_name,
            filename
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def upload_to_all_inbound_files(local_file_path: str, destination_filename) -> bool:
    try:
        return upload_blob(
            all_inbound_files_bucket_name,
            local_file_path,
            destination_filename
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return False


def file_exists_in_all_inbound_files(filename: str) -> bool:
    try:
        return blob_exists(
            all_inbound_files_bucket_name,
            filename
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return False


def file_exists_in_lab_reports(filename: str) -> bool:
    try:
        return blob_exists(
            lab_reports_bucket_name,
            filename
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return False


def file_exists_in_insurance_cards(filename: str) -> bool:
    try:
        return blob_exists(
            insurance_cards_bucket_name,
            filename
        )

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return False


def get_bucket_list():
    try:
        storage_client = storage.Client.from_service_account_json(
            service_account_file)
        buckets = list(storage_client.list_buckets())
        return buckets

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_file_list_in_bucket(bucket_name: str, prefix: str=''):
    try:
        storage_client = storage.Client.from_service_account_json(
            service_account_file)
        file_list = []
        for blob in storage_client.list_blobs(bucket_name, prefix=prefix):
            file_list.append(str(blob))

        return file_list

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
        return None


def blob_exists(bucket_name: str, filename: str) -> bool:
    try:
        storage_client = storage.Client.from_service_account_json(
            service_account_file)
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(filename)
        return blob.exists()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            bucket_name=bucket_name,
            filename=filename,
            function=whoami(),
            error=err
        )
        return False


def get_file_blob(bucket_name: str, filename: str):
    try:
        storage_client = storage.Client.from_service_account_json(
            service_account_file_prod)
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(filename)
        if blob.exists():
            return blob

    except Exception as err:
        log_generic(
            type=c.ERROR,
            bucket_name=bucket_name,
            filename=filename,
            function=whoami(),
            error=err
        )
        return None


def get_signed_url(bucket_name,
                         object_name,
                         subresource=None,
                         expiration=None,
                         http_method='GET',
                         query_parameters=None,
                         headers=None):
    try:
        if expiration is None:
            expiration = default_link_expiration_time_limit

        # Expiration Time can't exceed 604800 seconds (7 days)
        if expiration > 604800:
            return False

        if blob_exists(bucket_name, object_name):
            escaped_object_name = quote(
                six.ensure_binary(object_name), safe=b'/~')
            canonical_uri = '/{}'.format(escaped_object_name)

            datetime_now = datetime.datetime.utcnow()
            request_timestamp = datetime_now.strftime('%Y%m%dT%H%M%SZ')
            datestamp = datetime_now.strftime('%Y%m%d')

            google_credentials = service_account.Credentials.from_service_account_file(
                service_account_file)
            client_email = google_credentials.service_account_email
            credential_scope = '{}/auto/storage/goog4_request'.format(
                datestamp)
            credential = '{}/{}'.format(client_email, credential_scope)

            if headers is None:
                headers = dict()

            host = '{}.storage.googleapis.com'.format(bucket_name)
            headers['host'] = host

            canonical_headers = ''
            ordered_headers = collections.OrderedDict(sorted(headers.items()))
            for k, v in ordered_headers.items():
                lower_k = str(k).lower()
                strip_v = str(v).lower()
                canonical_headers += '{}:{}\n'.format(lower_k, strip_v)

            signed_headers = ''
            for k, _ in ordered_headers.items():
                lower_k = str(k).lower()
                signed_headers += '{};'.format(lower_k)
            signed_headers = signed_headers[:-1]  # remove trailing ';'

            if query_parameters is None:
                query_parameters = dict()
            query_parameters['X-Goog-Algorithm'] = 'GOOG4-RSA-SHA256'
            query_parameters['X-Goog-Credential'] = credential
            query_parameters['X-Goog-Date'] = request_timestamp
            query_parameters['X-Goog-Expires'] = expiration
            query_parameters['X-Goog-SignedHeaders'] = signed_headers
            if subresource:
                query_parameters[subresource] = ''

            canonical_query_string = ''
            ordered_query_parameters = collections.OrderedDict(
                sorted(query_parameters.items()))
            for k, v in ordered_query_parameters.items():
                encoded_k = quote(str(k), safe='')
                encoded_v = quote(str(v), safe='')
                canonical_query_string += '{}={}&'.format(encoded_k, encoded_v)
            # remove trailing '&'
            canonical_query_string = canonical_query_string[:-1]

            canonical_request = '\n'.join([http_method,
                                           canonical_uri,
                                           canonical_query_string,
                                           canonical_headers,
                                           signed_headers,
                                           'UNSIGNED-PAYLOAD'])

            canonical_request_hash = hashlib.sha256(
                canonical_request.encode()).hexdigest()

            string_to_sign = '\n'.join(['GOOG4-RSA-SHA256',
                                        request_timestamp,
                                        credential_scope,
                                        canonical_request_hash])

            # signer.sign() signs using RSA-SHA256 with PKCS1v15 padding
            signature = binascii.hexlify(
                google_credentials.signer.sign(string_to_sign)
            ).decode()

            scheme_and_host = '{}://{}'.format('https', host)
            signed_url = '{}{}?{}&x-goog-signature={}'.format(
                scheme_and_host, canonical_uri, canonical_query_string, signature)

            log_generic(
                type=c.INFO,
                bucket_name=bucket_name,
                object_name=object_name,
                signed_url=signed_url,
                function=whoami()
            )

            return signed_url

    except Exception as err:
        log_generic(
            type=c.ERROR,
            bucket_name=bucket_name,
            object_name=object_name,
            expiration=expiration,
            function=whoami(),
            error=err
        )
        return None


def upload_blob(bucket_name: str, source_filename: str, destination_blob_name: str) -> bool:
    if blob_exists(bucket_name, destination_blob_name):
        #print('file_exists -- skipping')
        return False
    try:
        storage_client = storage.Client.from_service_account_json(
            service_account_file)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_filename)

        log_generic(
            type=c.INFO,
            bucket_name=bucket_name,
            source_filename=source_filename,
            destination_blob_name=destination_blob_name,
            function=whoami()
        )
        return True

    except Exception as err:
        if err[0] and err[0] == 21:
            #print('Is a Directory')
            pass
        else:
            log_generic(
                type=c.ERROR,
                bucket_name=bucket_name,
                source_filename=source_filename,
                destination_blob_name=destination_blob_name,
                function=whoami(),
                error=err
            )
        return False


def upload_blob_from_string(bucket_name: str, base64string: str, content_type: str, destination_blob_name: str) -> bool:
    if blob_exists(bucket_name, destination_blob_name):
        #print('file_exists -- skipping')
        return False
    try:
        storage_client = storage.Client.from_service_account_json(
            service_account_file)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(
            base64.b64decode(base64string),
            content_type
        )

        log_generic(
            type=c.INFO,
            bucket_name=bucket_name,
            destination_blob_name=destination_blob_name,
            function=whoami()
        )
        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            bucket_name=bucket_name,
            base64string=base64string,
            destination_blob_name=destination_blob_name,
            function=whoami(),
            error=err
        )
        return False
