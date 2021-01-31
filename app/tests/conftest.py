import os
import sys
import pytest


myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from ggt.lib.utils import get_config_val
from ggt.lib.db import exec_delete, exec_insert
import tests.data as data


def insert(table, values):
    print("Inserting into table:", table)
    sql = """insert into {} values (""".format(table)
    field_values = list(values.values())
    values_formatted_string = """%s, """ * (len(field_values) - 1) + "%s)"
    sql += values_formatted_string
    print(sql)
    print(field_values)
    exec_insert(sql, tuple(field_values))


@pytest.fixture(scope='session')
def cleanup_db():
    env = get_config_val('env')

    if env != "TEST":
        pytest.exit('NOT A TEST ENVIRONMENT')
    tables = ['locations', 'groups', 'schedules', 'appointments', 'group_codes_to_locations_mapping',
            'patients', 'test_samples', 'states', 'services_catalog', 'services_to_locations_mapping', 'schedule_generation_rules',
            'workstations', 'users', 'insurance_info', 'appointment_services', 'organizations',
              'patient_questionnaires', 'locations_metrics_cache', 'schedules_metrics_cache', 'patient_consultations',
              'group_codes_to_locations_mapping', 'ggt_users', 'result_notification_campaigns', 'patient_questionnaires']
    for table in tables[::-1]:
        print("Cleaning up table:", table)
        sql = """delete from {} where id > -1""".format(table)
        exec_delete(sql)


@pytest.fixture(autouse=True, scope='session')
def test_populate_db(cleanup_db):
    for row in data.locations:
        insert('locations', row)
    for row in data.groups:
        insert('groups', row)
    for row in data.group_codes_to_locations_mapping:
        insert('group_codes_to_locations_mapping', row)
    for row in data.schedules:
        insert('schedules', row)
    for row in data.patients:
        insert('patients', row)
    for row in data.appointments:
        insert('appointments', row)
    for row in data.test_samples:
        insert('test_samples', row)
    for row in data.states:
        insert('states', row)
    for row in data.services_catalog:
        insert('services_catalog', row)
    for row in data.services_to_locations_mapping:
        insert('services_to_locations_mapping', row)
    for row in data.workstations:
        insert('workstations', row)
    for row in data.users:
        insert('users', row)
    for row in data.appointment_services:
        insert('appointment_services', row)
    for row in data.organizations:
        insert('organizations', row)
    for row in data.patient_questionnaires:
        insert('patient_questionnaires', row)
    for row in data.locations_metrics_cache:
        insert('locations_metrics_cache', row)
    for row in data.schedules_metrics_cache:
        insert('schedules_metrics_cache', row)
    for row in data.patient_consultations:
        insert('patient_consultations', row)
    for row in data.group_codes_to_locations_mapping:
        insert('group_codes_to_locations_mapping', row)
    for row in data.ggt_users:
        insert('ggt_users', row)
    for row in data.result_notification_campaigns:
        insert('result_notification_campaigns', row)
    for row in data.patient_questionnaires:
        insert('patient_questionnaires', row)
