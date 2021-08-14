import unittest

from ggt.models.data_models.billers import get_billing_list


class BillerSQLTests(unittest.TestCase):

    def test_get_billing_list(self):
        result = get_billing_list(0)

        result = get_billing_list(offset=2, status='pending')

        print(result)

