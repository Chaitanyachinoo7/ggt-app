import unittest

from ggt.models.data_models.data_types import FilterUser, FilterOrg
from ggt.models.data_models.management import list_org_requests, list_org_requests_v2, list_user, list_user_v2, \
    list_organizations, list_organizations_v2


class OrgRequest:
    status = ''


class LabSQLTests(unittest.TestCase):

    def test_list_org_requests(self):

        result = list_org_requests(OrgRequest())
        result_2 = list_org_requests_v2(OrgRequest())

        print(result)
        self.assertEqual(result, result_2)

        request = OrgRequest()
        request.status = 'pending'

        result = list_org_requests(request)
        result_2 = list_org_requests_v2(request)

        print(result)
        self.assertEqual(result, result_2)

    def test_list_user(self):

        filterUser = FilterUser(role='admin', name='', email='')

        result = list_user(filterUser, {})
        result_2 = list_user_v2(filterUser, {})

        print(result)
        self.assertEqual(result, result_2)

        filterUser = FilterUser(role='admin', name='t', email='')

        result = list_user(filterUser, {})
        result_2 = list_user_v2(filterUser, {})

        print(result)
        self.assertEqual(result, result_2)

    def test_list_organizations(self):

        filterOrg = FilterOrg(name='')

        result = list_organizations(filterOrg, {})
        result_2 = list_organizations_v2(filterOrg, {})

        print(result)
        self.assertEqual(result, result_2)

        filterOrg = FilterOrg(name='Test')

        result = list_organizations(filterOrg, {})
        result_2 = list_organizations_v2(filterOrg, {})

        print(result)
        self.assertEqual(result, result_2)

