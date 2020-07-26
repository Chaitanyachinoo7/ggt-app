'''
from faker import Faker

faker = Faker()

for x in range(765):
  print("{}\t{}\t{}".format(faker.first_name(), faker.last_name(), faker.date()))

'''

'''
import pysftp
host = "sftp.healthtrackrx.com"

username = "wellpay"
password = "9cTE3fh@8H"
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

with pysftp.Connection(host, username=username, password=password, cnopts=cnopts) as sftp:
  print ("Connection succesfully stablished ... ")


'''

from google.cloud import storage

# Explicitly use service account credentials by specifying the private key
# file.
storage_client = storage.Client.from_service_account_json(
    'test-creds.json')


def explicit():
    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)


def blob_exists(bucket_name, filename):
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    return blob.exists()



def generate_signed_url(bucket_name, 
                        object_name,
                        subresource=None, 
                        expiration=300, 
                        http_method='GET',
                        query_parameters=None, 
                        headers=None):
    import datetime
    import six
    from six.moves.urllib.parse import quote
    from google.oauth2 import service_account
    import collections
    import hashlib
    import binascii

    if expiration > 300:
        # print('Expiration Time can\'t be longer than 604800 seconds (7 days).')
        #sys.exit(1)
        print('error')
    if blob_exists(bucket_name, object_name):
        escaped_object_name = quote(six.ensure_binary(object_name), safe=b'/~')
        canonical_uri = '/{}'.format(escaped_object_name)

        datetime_now = datetime.datetime.utcnow()
        request_timestamp = datetime_now.strftime('%Y%m%dT%H%M%SZ')
        datestamp = datetime_now.strftime('%Y%m%d')


        google_credentials = service_account.Credentials.from_service_account_file(
            'test-creds.json')
        client_email = google_credentials.service_account_email
        credential_scope = '{}/auto/storage/goog4_request'.format(datestamp)
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

        return signed_url
    else:
        return ""




def upload_blob(bucket_name, source_file_name, destination_blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )



explicit()
if blob_exists('ggt-lab-reports', 'Final-Report-InfectiousDisease_sum-1605152-353806-20200716033342-26964.pdf'):
  print('exists')
if blob_exists('ggt-lab-reports', '1605152-353806-20200716033342-26964.pdf'):
  print('exists')

print(generate_signed_url('ggt-lab-reports', 'Final-Report-InfectiousDisease_sum-1605152-353806-20200716033342-26964.pdf'))



