import unittest

from ggt.models.data_models.billers import get_billing_list, get_billing_list_v2


class BillerSQLTests(unittest.TestCase):

    def test_get_billing_list(self):

        result = get_billing_list(0)
        result_2 = get_billing_list_v2(0)

        self.assertEqual(result, result_2)

        result = get_billing_list(offset=2, status='pending')
        result_2 = get_billing_list_v2(offset=2, status='pending')

        print(result)
        self.assertEqual(result, result_2)
