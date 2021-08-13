import unittest

from ggt.models.data_models.schedules import reject_certificate_v2, get_patient_by_id, get_patient_by_id_v2, \
    lookup_certificate, lookup_certificate_v2


class SchedulesSQLTests(unittest.TestCase):

    def test_reject_certificate(self):
        result = reject_certificate_v2([938669, 938657])

        print(result)
        # self.assertEqual(result, result_2)

    def test_get_patient_by_id(self):
        result = get_patient_by_id(123469)
        result_2 = get_patient_by_id_v2(123469)

        print(result)
        self.assertEqual(result, result_2)

    def test_lookup_certificate(self):
        self.maxDiff = None

        result = lookup_certificate("+15108464944", "", "", "")
        result_2 = lookup_certificate_v2("+15108464944", "", "", "")

        print(result)
        self.assertTupleEqual(result, result_2)

