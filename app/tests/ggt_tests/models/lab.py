import unittest

from ggt.models.data_models.lab import get_verification_level_from_patient_id


class LabSQLTests(unittest.TestCase):

    def test_get_verification_level_from_patient_id(self):

        result = get_verification_level_from_patient_id(840232)

        print(result)

