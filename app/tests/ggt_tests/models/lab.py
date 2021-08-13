import unittest

from ggt.models.data_models.lab import get_verification_level_from_patient_id, get_verification_level_from_patient_id_v2


class LabSQLTests(unittest.TestCase):

    def test_get_verification_level_from_patient_id(self):

        result = get_verification_level_from_patient_id(840232)
        result_2 = get_verification_level_from_patient_id_v2(840232)

        print(result)
        self.assertEqual(result, result_2)
