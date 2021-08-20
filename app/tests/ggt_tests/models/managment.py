import unittest

from ggt.models.data_models.data_types import FilterUser, FilterOrg
from ggt.models.data_models.management import list_org_requests, list_user, \
    list_organizations


class OrgRequest:
    status = ''


class LabSQLTests(unittest.TestCase):

    def test_list_org_requests(self):

        result = list_org_requests(OrgRequest())

        print(result)

        request = OrgRequest()
        request.status = 'pending'

        result = list_org_requests(request)

        print(result)

    def test_list_user(self):

        filterUser = FilterUser(role='admin', name='', email='')

        result = list_user(filterUser, {})

        print(result)

        filterUser = FilterUser(role='admin', name='t', email='')

        result = list_user(filterUser, {})

        print(result)

    def test_list_organizations(self):

        filterOrg = FilterOrg(name='')

        result = list_organizations(filterOrg, {})

        print(result)

        filterOrg = FilterOrg(name='Test')

        result = list_organizations(filterOrg, {})

        print(result)

