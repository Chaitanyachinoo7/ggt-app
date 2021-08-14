import unittest

from ggt.models.data_models.schedules import reject_certificate, get_patient_by_id, \
    lookup_certificate, vax_yes_activity, \
    get_slots_matching_dt_list, \
    get_available_locations_near_lat_lng, get_available_locations_near_lat_lng_v2


class SchedulesSQLTests(unittest.TestCase):

    def test_reject_certificate(self):
        result = reject_certificate([938669])

        print(result)
        # self.assertEqual(result, result_2)

    def test_get_patient_by_id(self):
        result = get_patient_by_id(123469)

        print(result)

    def test_lookup_certificate(self):


        result = lookup_certificate("", "", "Donald", "")

        # result = lookup_certificate("", "", "Charity", "")
        # result_2 = lookup_certificate_v2("", "", "Charity", "")
        #
        # print(result)
        # self.assertEqual(result, result_2)
        #
        # result = lookup_certificate("", "", "Donald", "", verification_level=1)
        # result_2 = lookup_certificate_v2("", "", "Donald", "", verification_level=1)
        #
        # print(result)
        # self.assertEqual(result, result_2)

    def test_vax_yes_activity(self):

        result = vax_yes_activity(939004, "")

        print(result)

        result = vax_yes_activity("", "143723090141")

        print(result)

    def test_get_slots_matching_dt_list(self):

        result = get_slots_matching_dt_list(['2020-11-19 09:16:00'], 222, '')

        print(result)
        # for idx, item in enumerate(result):
        #     self.assertEqual(item.id, result_2[idx].id)
        #     self.assertEqual(item.location_id, result_2[idx].location_id)
        #     self.assertEqual(item.start_dt, result_2[idx].start_dt)
        #     self.assertEqual(item.end_dt, result_2[idx].end_dt)
        #     self.assertEqual(item.duration, result_2[idx].duration)
        #     self.assertEqual(item.status, result_2[idx].status)
        #     self.assertEqual(item.appointment_id, result_2[idx].appointment_id)

        result = get_slots_matching_dt_list(['2020-11-19 09:16:00', '2020-11-19 09:00:00'], 222, '')

        print(result)
        # for idx, item in enumerate(result):
        #     self.assertEqual(item.id, result_2[idx].id)
        #     self.assertEqual(item.location_id, result_2[idx].location_id)
        #     self.assertEqual(item.start_dt, result_2[idx].start_dt)
        #     self.assertEqual(item.end_dt, result_2[idx].end_dt)
        #     self.assertEqual(item.duration, result_2[idx].duration)
        #     self.assertEqual(item.status, result_2[idx].status)
        #     self.assertEqual(item.appointment_id, result_2[idx].appointment_id)

    def test_get_available_locations(self):

        result = get_available_locations_near_lat_lng(32, 96, 10000, '2020-11-12', 'LOWES', False)

        result_2 = get_available_locations_near_lat_lng_v2(32, 96, 10000, '2020-11-12', 'LOWES', False)
        print(result)
        self.assertEqual(result, result_2)

    def test_lock_certificate(self):
        """
            private method testing
        """
        # result = lock_record([938678])
        #resul_2 = lock_record_v2([938679, 938678])



