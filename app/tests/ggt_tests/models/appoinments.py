import unittest

from ggt.models.data_models.appointments import add_service_to_appointment, add_service_to_appointment_v2, \
    get_appointment, get_appointment_v2, lookup_certificate ,lookup_certificate_v2, \
    lookup_pkpass, lookup_pkpass_v2


class AppointmentSQLTests(unittest.TestCase):

    def test_add_service_to_appointment(self):

        result = add_service_to_appointment(12345, 'COVID_19_TEST')
        result_2 = add_service_to_appointment_v2(12345, 'COVID_19_TEST')

        self.assertEqual(result, result_2)
        self.assertEqual(result, True)
        self.assertEqual(result_2, True)

    def test_get_appointment(self):
        result = get_appointment(22, 1)
        result_2 = get_appointment_v2(22, 1)

        self.assertEqual(result, result_2)

        self.assertEqual(result.id, 22)
        self.assertEqual(result_2.id, 22)

        self.assertEqual(result.org_name, 'GoGetTested')
        self.assertEqual(result_2.org_name, 'GoGetTested')

        try:
            get_appointment(22, 0)
            self.fail()
        except Exception as e:
            self.assertNotEqual(e, None)

        try:
            get_appointment_v2(22, 0)
            self.fail()
        except Exception as e:
            self.assertNotEqual(e, None)

    def test_lookup_certificate(self):
        result = lookup_certificate('+18137664031', "", "", "")
        result_2 = lookup_certificate_v2('+18137664031', "", "", "")

        self.assertEqual(result, result_2)

        result = lookup_certificate('+18137664031', "", "Charity", "")
        result_2 = lookup_certificate_v2('+18137664031', "", "Charity", "")

        self.assertEqual(result, result_2)

        result = lookup_certificate('', "", "Charity", "Nickerson")
        result_2 = lookup_certificate_v2('', "", "Charity", "Nickerson")

        self.assertEqual(result, result_2)

        result = lookup_certificate('', "1978-11-09", "", "Nickerson")
        result_2 = lookup_certificate_v2('', "1978-11-09", "", "Nickerson")

        self.assertEqual(result, result_2)


    def test_lookup_pkpass(self):
        result = lookup_pkpass("+18137664031", "1978-11-0", "Charity", "Nickerson", "dee0e237-ed12-4bc6-a3b3-95b6f292ceb4")
        result_2 = lookup_pkpass_v2("+18137664031", "1978-11-0", "Charity", "Nickerson", "dee0e237-ed12-4bc6-a3b3-95b6f292ceb4")

        # Values are not received by either of the methods as the tokens are invalid, this is only to validate the query
        self.assertEqual(result, result_2)
        self.assertEqual(result, {})








