import sqlite3
from sqlite3 import Error
import json

from ggt.lib.utils import (
    get_config_val,
    log_generic
)

sqlite_db = get_config_val('databases.sqlite.tasks_sqlite_db')


def init_local_cache():
    print('Initializing Local Cache -- {}'.format(sqlite_db))
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    CREATE TABLE IF NOT EXISTS all_inbound_files (
                        filename  VARCHAR UNIQUE);
                    ''')
        c.execute('''
                    CREATE TABLE IF NOT EXISTS files_in_remote_storage (
                        filename  VARCHAR UNIQUE);
                    ''')
        c.execute('''
                    CREATE TABLE IF NOT EXISTS lab_test_records (
                        requisition_id  INTEGER PRIMARY KEY,
                        order_number    VARCHAR,
                        first_name      VARCHAR,
                        last_name       VARCHAR,
                        dob             VARCHAR,
                        assay_name      VARCHAR,
                        status          VARCHAR,
                        result          VARCHAR);
                    ''')
        c.execute('''
                    CREATE TABLE IF NOT EXISTS csv_pdf_sync (
                        requisition_id	INTEGER PRIMARY KEY,
                        order_number    VARCHAR,
                        first_name      VARCHAR,
                        last_name       VARCHAR,
                        dob             VARCHAR,
                        assay_name      VARCHAR,
                        status          VARCHAR,
                        result          VARCHAR,
                        has_pdf         INTEGER,
                        has_csv         INTEGER);
                    ''')
        conn.commit()
    except Exception as err:
        log_generic(
            type="error",
            function='init_local_cache',
            error=err)
    finally:
        conn.close()


def add_to_lab_test_records_cache(rec):
    result = False
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        sql = '''
            INSERT OR IGNORE INTO lab_test_records
            (requisition_id, order_number, first_name,
             last_name, dob, assay_name, status, result)
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
        '''.format(
            str(rec['requisition_id']),
            str(rec['order_number']),
            str(rec['first_name']).replace('"', r'\"').replace("'", "''"),
            str(rec['last_name']).replace('"', r'\"').replace("'", "''"),
            str(rec['dob']),
            str(rec['assay_name']),
            str(rec['status']),
            str(rec['result'])
        )
        c.execute(sql)
        conn.commit()
        result = True
    except Exception as err:
        log_generic(
            type="error",
            rec=rec,
            function='add_to_lab_test_records_cache',
            error=err)
    finally:
        conn.close()

    return result


def add_to_csv_pdf_sync_cache(rec, source='csv'):
    if is_present_in_csv_pdf_sync_cache(str(rec['requisition_id'])):
        update_csv_pdf_sync_cache(rec, source)
    else:
        insert_into_csv_pdf_sync_cache(rec, source)


def insert_into_csv_pdf_sync_cache(rec, source):
    result = False
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()

        if source == 'csv':
            sql = '''
                INSERT OR IGNORE INTO csv_pdf_sync
                (requisition_id, order_number, first_name, last_name, dob, assay_name, status, result, has_csv)
                VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', 1)
            '''.format(
                str(rec['requisition_id']),
                str(rec['order_number']),
                str(rec['first_name']).replace('"', r'\"').replace("'", "''"),
                str(rec['last_name']).replace('"', r'\"').replace("'", "''"),
                str(rec['dob']),
                str(rec['assay_name']),
                str(rec['status']),
                str(rec['result'])
            )
        else:
            sql = '''
                INSERT OR IGNORE INTO csv_pdf_sync
                (requisition_id, has_pdf)
                VALUES ('{}', 1)
            '''.format(
                str(rec['requisition_id'])
            )

        c.execute(sql)
        conn.commit()
        result = True

    except Exception as err:
        log_generic(
            type="error",
            rec=rec,
            function='insert_into_csv_pdf_sync_cache',
            error=err)
    finally:
        conn.close()

    return result


def update_csv_pdf_sync_cache(rec, source='csv'):
    result = False
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()

        if source == 'csv':
            sql = '''
                UPDATE csv_pdf_sync
                SET 
                    order_number = '{}',
                    first_name = '{}',
                    last_name = '{}',
                    dob = '{}',
                    assay_name = '{}',
                    status = '{}',
                    result = '{}',
                    has_csv = 1
                WHERE 
                    requisition_id = {}
            '''.format(
                str(rec['order_number']),
                str(rec['first_name']).replace('"', r'\"').replace("'", "''"),
                str(rec['last_name']).replace('"', r'\"').replace("'", "''"),
                str(rec['dob']),
                str(rec['assay_name']),
                str(rec['status']),
                str(rec['result']),
                str(rec['requisition_id'])
            )
        else:
            sql = '''
                UPDATE csv_pdf_sync
                SET 
                    has_pdf = 1
                WHERE 
                    requisition_id = {}
            '''.format(
                str(rec['requisition_id'])
            )

        c.execute(sql)
        conn.commit()
        result = True

    except Exception as err:
        log_generic(
            type="error",
            rec=rec,
            sql=sql,
            function='update_csv_pdf_sync_cache',
            error=err)
    finally:
        conn.close()

    return result


def is_present_in_csv_pdf_sync_cache(requisition_id):
    status = False
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    SELECT COUNT(*)
                    FROM csv_pdf_sync
                    where requisition_id = {}
                '''.format(requisition_id))
        row = c.fetchone()
        if row[0] > 0:
            status = True

    except Exception as err:
        log_generic(
            type="error",
            requisition_id=requisition_id,
            function='is_present_in_csv_pdf_sync_cache',
            error=err)
    finally:
        conn.close()

    return status


def get_order_number_by_requisition_id(requisition_id):
    result = None
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    SELECT order_number
                    FROM lab_test_records
                    where requisition_id = {}
                '''.format(requisition_id))
        row = c.fetchone()
        result = row[0]

    except Exception as err:
        if err[0] and err[0] == "'NoneType' object is not subscriptable":
            pass  # This is expected for missing Requisition IDs
        else:
            log_generic(
                type="error",
                requisition_id=requisition_id,
                function='get_order_number_by_requisition_id',
                error=err)
    finally:
        conn.close()

    return result


def get_all_lab_records_from_cache():
    result = False
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    SELECT *
                    FROM lab_test_records
                    WHERE status IN ('Approved', 'Resulted')
                ''')
        rows = c.fetchall()
        result = rows

    except Exception as err:
        log_generic(
            type="error",
            function='get_all_lab_records_from_cache',
            error=err)
    finally:
        conn.close()

    return result


def add_to_all_inbound_files_cache(filename):
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    INSERT OR IGNORE INTO all_inbound_files 
                    (filename) 
                    VALUES ('{}')
                '''.format(
            filename
        ))
        conn.commit()
    except Exception as err:
        log_generic(
            type="error",
            filename=filename,
            function='add_to_all_inbound_files_cache',
            error=err)
    finally:
        conn.close()

    return True


def file_exists_in_all_inbound_files_cache(filename):
    row = []
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    SELECT count(*) 
                    FROM all_inbound_files
                    WHERE filename = '{}'
                '''.format(
            filename
        ))
        row = c.fetchone()
        conn.close()

    except Exception as err:
        log_generic(
            type="error",
            filename=filename,
            function='file_exists_in_all_inbound_files_cache',
            error=err)
    finally:
        conn.close()

    if row[0] > 0:
        return True
    else:
        return False


'''adds to cache if remote storage indicated that the file exists there'''


def add_to_files_in_remote_storage_cache(filename):
    result = False
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    INSERT OR IGNORE INTO files_in_remote_storage 
                    (filename) 
                    VALUES ('{}')
                '''.format(
            filename
        ))
        conn.commit()
        result = True
    except Exception as err:
        log_generic(
            type="error",
            filename=filename,
            function='add_to_files_in_remote_storage_cache',
            error=err)
    finally:
        conn.close()

    return result


def file_exists_in_files_in_remote_storage_cache(filename):
    result = False
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    SELECT count(*) 
                    FROM files_in_remote_storage
                    WHERE filename = '{}'
                '''.format(
            filename
        ))
        row = c.fetchone()

        if row and row[0] > 0:
            result = True

    except Exception as err:
        log_generic(
            type="error",
            filename=filename,
            function='file_exists_in_files_in_remote_storage_cache',
            error=err)
    finally:
        conn.close()

    return result
