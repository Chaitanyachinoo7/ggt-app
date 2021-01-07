import sqlite3
from sqlite3 import Error
import ujson

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

import ggt.lib.constants as c

sqlite_db = get_config_val('databases.sqlite.tasks_sqlite_db')


def init_local_cache():
    print('Initializing Local Cache -- {}'.format(sqlite_db))
    try:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS all_inbound_files (
                        filename  VARCHAR UNIQUE);
                    ''')
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS files_in_remote_storage (
                        filename  VARCHAR UNIQUE);
                    ''')
        cur.execute('''
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
        cur.execute('''
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
            type=c.ERROR,
            function=whoami(),
            error=err
        )
    finally:
        conn.close()


def add_to_lab_test_records_cache(rec):
    result = False
    try:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()
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
        cur.execute(sql)
        conn.commit()
        result = True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            rec=rec,
            function=whoami(),
            error=err
        )
    finally:
        conn.close()

    return result


def add_to_csv_pdf_sync_cache(rec, source='csv'):
    if is_present_in_csv_pdf_sync_cache(str(rec['requisition_id'])):
        update_csv_pdf_sync_cache(rec, source)
    else:
        insert_into_csv_pdf_sync_cache(rec, source)


def add_to_lab_test_records_cache_v2(requisition_id, order_number, result, status):
    res = False
    try:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()
        sql = '''
            INSERT OR IGNORE INTO lab_test_records
            (requisition_id, order_number, status, result)
            VALUES ('{}', '{}', '{}', '{}')
        '''.format(
                requisition_id,
                order_number,
                status,
                result
        )
        cur.execute(sql)
        conn.commit()
        res = True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            rec=rec,
            function=whoami(),
            error=err
        )
    finally:
        conn.close()

    return res


def add_to_csv_pdf_sync_cache_v2(requisition_id, order_number, result, status):
    res = False
    try:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()

        sql = '''
            INSERT OR IGNORE INTO csv_pdf_sync
            (requisition_id, order_number, status, result, has_csv, has_pdf)
            VALUES ('{}', '{}', '{}', '{}', 1, 1)
        '''.format(
                requisition_id,
                order_number,
                status,
                result
            )

        cur.execute(sql)
        conn.commit()
        res = True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            rec=rec,
            function=whoami(),
            error=err
        )
    finally:
        conn.close()

    return res


def insert_into_csv_pdf_sync_cache(rec, source):
    result = False
    try:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()

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

        cur.execute(sql)
        conn.commit()
        result = True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            rec=rec,
            function=whoami(),
            error=err
        )
    finally:
        conn.close()

    return result


def update_csv_pdf_sync_cache(rec, source='csv'):
    result = False
    try:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()

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

        cur.execute(sql)
        conn.commit()
        result = True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            rec=rec,
            sql=sql,
            function=whoami(),
            error=err
        )
    finally:
        conn.close()

    return result


def is_present_in_csv_pdf_sync_cache(requisition_id):
    status = False
    try:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()
        cur.execute('''
                    SELECT COUNT(*)
                    FROM csv_pdf_sync
                    where requisition_id = {}
                '''.format(requisition_id))
        row = cur.fetchone()
        if row[0] > 0:
            status = True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            requisition_id=requisition_id,
            function=whoami(),
            error=err
        )
    finally:
        conn.close()

    return status


def get_order_number_by_requisition_id(requisition_id):
    result = None
    try:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()
        cur.execute('''
                    SELECT order_number
                    FROM lab_test_records
                    where requisition_id = {}
                '''.format(requisition_id))
        row = cur.fetchone()

        if row:
            result = row[0]

    except Exception as err:
        log_generic(
            type=c.ERROR,
            requisition_id=requisition_id,
            function=whoami(),
            error=err
        )
    finally:
        conn.close()

    return result


def get_all_lab_records_from_cache():
    result = False
    try:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()
        cur.execute('''
                    SELECT *
                    FROM lab_test_records
                    WHERE status IN ('Approved', 'Resulted', 'Rejected', 'approved', 'resulted', 'rejected')
                ''')
        rows = cur.fetchall()
        result = rows

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
    finally:
        conn.close()

    return result


def add_to_all_inbound_files_cache(filename):
    try:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()
        cur.execute('''
                    INSERT OR IGNORE INTO all_inbound_files 
                    (filename) 
                    VALUES ('{}')
                '''.format(
            filename
        ))
        conn.commit()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            filename=filename,
            function=whoami(),
            error=err
        )
    finally:
        conn.close()

    return True


def file_exists_in_all_inbound_files_cache(filename):
    row = []
    try:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()
        cur.execute('''
                    SELECT count(*) 
                    FROM all_inbound_files
                    WHERE filename = '{}'
                '''.format(
            filename
        ))
        row = cur.fetchone()
        conn.close()

    except Exception as err:
        log_generic(
            type=c.ERROR,
            filename=filename,
            function=whoami(),
            error=err
        )
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
        cur = conn.cursor()
        cur.execute('''
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
            type=c.ERROR,
            filename=filename,
            function=whoami(),
            error=err
        )
    finally:
        conn.close()

    return result


def file_exists_in_files_in_remote_storage_cache(filename):
    result = False
    try:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()
        cur.execute('''
                    SELECT count(*) 
                    FROM files_in_remote_storage
                    WHERE filename = '{}'
                '''.format(
            filename
        ))
        row = cur.fetchone()

        if row and row[0] > 0:
            result = True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            filename=filename,
            function=whoami(),
            error=err
        )
    finally:
        conn.close()

    return result
