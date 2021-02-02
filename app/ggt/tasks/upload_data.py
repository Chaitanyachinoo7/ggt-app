import csv
import pathlib
from datetime import datetime
# ORGANIZATION_ID = 1
# SEASON_ID = 1
# PATH = pathlib.Path(__file__).parent.absolute()

from ggt.lib.adapters.mysql_adapter import exec_batch_execute


def inject_selected_patients():
    with open('data/selected_patients') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        patients = []
        for row in csv_reader:
            l = len(row)
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')

            else:
                d = datetime.strptime(row[0], "%m/%d/%Y")
                patient = (d, row[l-1], True)
                patients.append(patient)
            line_count += 1
        print('*****************************Injecting selected_patients*************************')
        sql = """INSERT INTO temp_selected_patients (dob, email, is_available) VALUES (%s, %s, %s);"""
        inserted = exec_batch_execute(sql, tuple(patients))
        if inserted:
            print('*****************************selected_patients Injected**************************')
        else:
            print('*****************************selected_patients Injection Failed*******************')


inject_selected_patients()