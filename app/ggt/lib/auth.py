from google.oauth2 import id_token
from google.auth.transport import requests

from ggt.lib.utils import (log_generic)

CLIENT_ID = "269165607649-ejpvn7ar1llub2e8tr6ur4ad2p1srucf.apps.googleusercontent.com"


def verify_google_idtoken(token):
    try:
        decoded_token = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        if(decoded_token['email'].split('@')[1] == "wellpay.com" or
           decoded_token['email'].split('@')[1] == "wellhealth.studio" or
           decoded_token['email'].split('@')[1] == "hrmdmanagement.com" or
           decoded_token['email'].split('@')[1] == "flowermoundpain.co"):
            return True
        else:
            return False

    except Exception as err:
        log_generic(
            type="error", 
            token=token, 
            function='verify_google_idtoken', 
            error=err)
        return False
