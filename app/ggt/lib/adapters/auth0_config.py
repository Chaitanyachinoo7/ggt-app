from ggt.lib.utils import get_config_val as cfg


AUTH0_DOMAIN = cfg('vendors.auth0.auth0_domain')
API_AUDIENCE = cfg('vendors.auth0.api_audience')
AUTH0_MANAGEMENT_CLIENT_ID = cfg('vendors.auth0.management_client_id')
AUTH0_MANAGEMENT_CLIENT_SECRET = cfg('vendors.auth0.management_sectret')
AUTH0_CONNECTION = cfg('vendors.auth0.connection')
ALGORITHMS = cfg('vendors.auth0.algorithms')
META_KEY = "http://roles.ggt/meta"
ORGANIZATION_KEY = "organization"

'''No need to define these variables in environment'''
AUTH0_MANAGEMENT_AUDIENCE = 'https://' + AUTH0_DOMAIN + '/api/v2/'
AUTH_URL = 'https://' + AUTH0_DOMAIN + '/oauth/token'
AUTH0_MANAGEMENT_GRANT_TYPE = "client_credentials"
AUTH0_USER_MANAGEMENT_API = 'https://' + AUTH0_DOMAIN + '/api/v2/users'
AUTH0_GET_ROLES_API = 'https://' + AUTH0_DOMAIN + '/api/v2/roles'
AUTH0_ASSIGN_ROLES_API = 'https://' + AUTH0_DOMAIN + '/api/v2/users/{}/roles'
AUTH0_USER_UPDATE_API = 'https://' + AUTH0_DOMAIN + '/api/v2/users/{}'