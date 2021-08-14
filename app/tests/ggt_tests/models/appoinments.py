import unittest

from ggt.models.data_models.appointments import add_service_to_appointment, \
    get_appointment, lookup_certificate, \
    lookup_pkpass


class AppointmentSQLTests(unittest.TestCase):

    def test_add_service_to_appointment(self):

        result = add_service_to_appointment(12345, 'COVID_19_TEST')

        self.assertEqual(result, True)

    def test_get_appointment(self):
        result = get_appointment(22, 1)

        self.assertEqual(result.id, 22)

        self.assertEqual(result.org_name, 'GoGetTested')

        try:
            get_appointment(22, 0)
            self.fail()
        except Exception as e:
            self.assertNotEqual(e, None)


    def test_lookup_certificate(self):
        result = lookup_certificate('+18137664031', "", "", "")

        result = lookup_certificate('+18137664031', "", "Charity", "")

        result = lookup_certificate('', "", "Charity", "Nickerson")

        result = lookup_certificate('', "1978-11-09", "", "Nickerson")



    def test_lookup_pkpass(self):
        result = lookup_pkpass("+18137664031", "1978-11-0", "Charity", "Nickerson", "dee0e237-ed12-4bc6-a3b3-95b6f292ceb4")
        self.assertEqual(result, {})








