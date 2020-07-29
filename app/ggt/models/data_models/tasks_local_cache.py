import sqlite3
from sqlite3 import Error

from ggt.lib.utils import (
    get_config_val,
    log_generic
)

sqlite_db = get_config_val('databases.sqlite.tasks_sqlite_db')

    
def init_local_cache():
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
        conn.commit()
    except Exception as err:
        log_generic(
            type="error", 
            function='init_local_cache', 
            error=err)
    finally:
        conn.close()



def add_to_lab_test_records_cache(rec):
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        sql = '''
            INSERT OR IGNORE INTO lab_test_records 
            (requisition_id, order_number, first_name, last_name, dob, assay_name, status, result) 
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
        '''.format(
                str(rec['requisition_id']), 
                str(rec['order_number']), 
                str(rec['first_name']), 
                str(rec['last_name']), 
                str(rec['dob']), 
                str(rec['assay_name']), 
                str(rec['status']), 
                str(rec['result'])
            )
        c.execute(sql)
        conn.commit()
    except Exception as err:
        log_generic(
            type="error", 
            function='init_local_cache', 
            error=err)
    finally:
        conn.close()



def get_order_number_by_requisition_id(requisition_id):
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    SELECT order_number
                    FROM lab_test_records
                    where requisition_id = {}
                '''.format(requisition_id))
        row = c.fetchone()
        return row[0]


    except Exception as err:
        log_generic(
            type="error", 
            function='init_local_cache', 
            error=err)
    finally:
        conn.close()


def get_all_lab_records_from_cache():
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    SELECT *
                    FROM lab_test_records
                ''')
        rows = c.fetchall()
        return rows

    except Exception as err:
        log_generic(
            type="error", 
            function='init_local_cache', 
            error=err)
    finally:
        conn.close()



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


def file_exists_in_all_inbound_files_cache(filename):
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

        if row[0]>0:
            return True
        else:
            return False

    except Exception as err:
        log_generic(
            type="error", 
            filename=filename,
            function='file_exists_in_all_inbound_files_cache', 
            error=err)
    finally:
        conn.close()




'''adds to cache if remote storage indicated that the file exists there'''
def add_to_files_in_remote_storage_cache(filename):
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
    except Exception as err:
        log_generic(
            type="error", 
            filename=filename,
            function='add_to_files_in_remote_storage_cache', 
            error=err)
    finally:
        conn.close()


def file_exists_in_files_in_remote_storage_cache(filename):
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
        conn.close()

        if row[0]>0:
            return True
        else:
            return False

    except Exception as err:
        log_generic(
            type="error", 
            filename=filename,
            function='file_exists_in_files_in_remote_storage_cache', 
            error=err)
    finally:
        conn.close()

