from ggt.lib.utils import get_config_val as cfg
import requests

# auth_id = cfg('vendors.smartystreets.auth_id')
# auth_token = cfg('vendors.smartystreets.auth_token')
# license = cfg('vendors.smartystreets.license')


def validate_us_address(street, city, state, zipcode):
    r = requests.get(
        "https://us-street.api.smartystreets.com/street-address?auth-id={}&auth-token={}&license={}&street={}&city={}&state={}&zipcode={}".format(auth_id, auth_token, license, street, city, state, zipcode))
    return len(r.json())


def validate_non_us_address(street, city, state, zipcode, country):
    r = requests.get(
        "https://international-street.api.smartystreets.com/verify?auth-id={}&auth-token={}&license={}&address1={}&locality={}&administrative_area={}&postal_code={}&country={}".format(auth_id, auth_token, license, street, city, state, zipcode, country))
    print(r.status_code)
    return len(r.json())
