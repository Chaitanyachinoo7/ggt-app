import sqlite3
from sqlite3 import Error


sqlite_db = '/tmp/ggt-tasks/ggt_local_cache.db'


    
def init_local_cache():
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    CREATE TABLE all_inbound_files (
                        filename  VARCHAR UNIQUE);
                    ''')
        c.execute('''
                    CREATE TABLE uploaded_pdf_files (
                        filename  VARCHAR UNIQUE);
                    ''')
        c.execute('''
                    CREATE TABLE processed_records (
                        requisition_id  INTEGER PRIMARY KEY,
                        order_number    VARCHAR,
                        first_name      VARCHAR,
                        last_name       VARCHAR,
                        dob             VARCHAR,
                        assay_name      VARCHAR,
                        status          VARCHAR,
                        result          VARCHAR,
                        processed       INTEGER);
                    ''')
        conn.commit()
        conn.close()
    except Exception as err:
        print(err)


def add_to_processed_records_cache(rec):
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    INSERT OR IGNORE INTO processed_records 
                    (requisition_id, order_number, first_name, last_name, dob, assay_name, status, result) 
                    VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', 0)
                '''.format(
                        str(rec['requisition_id']), 
                        str(rec['order_number']), 
                        str(rec['first_name']), 
                        str(rec['last_name']), 
                        str(rec['DOB']), 
                        str(rec['assay_name']), 
                        str(rec['status']), 
                        str(rec['result'])
                    ))
        conn.commit()
        conn.close()
    except Exception as err:
        print(err)


def mark_record_as_processed_in_records_cache(requisition_id):
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    UPDATE processed_records
                    SET 
                        processed = 1
                    WHERE
                        requisition_id = {}
                    '''.format(
                        requisition_id
                    ))
        conn.commit()
        conn.close()

    except Exception as err:
        print(err)

def record_exists_in_processed_records_cache(rec):
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    SELECT count(*) 
                    FROM processed_records
                    WHERE requisition_id = {}
                '''.format(
                        rec['requisition_id']
                ))
        row = c.fetchone()
        conn.commit()
        conn.close()
        if row[0]>0:
            return True
        else:
            return False

    except Exception as err:
        print(err)

def get_pending_records_from_processed_records_cache():
    try:
        conn = sqlite3.connect(sqlite_db)
        c = conn.cursor()
        c.execute('''
                    SELECT requisition_id, order_number, first_name, last_name, dob, assay_name, status, result
                    FROM processed_records
                    WHERE processed = 0
                '''
                )
        rows = c.fetchall()
        conn.commit()
        conn.close()

        return rows

    except Exception as err:
        print(err)

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
        conn.close()
    except Exception as err:
        print(err)


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
        conn.commit()
        conn.close()

        if row[0]>0:
            return True
        else:
            return False

    except Exception as err:
        print(err)

