import mysql.connector
from mysql.connector import Error

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

import ggt.lib.constants as c


writer_connection_config_dict = {
    'user': get_config_val('databases.mysql.username'),
    'password': get_config_val('databases.mysql.password'),
    'host': get_config_val('databases.mysql.host'),
    'database': get_config_val('databases.mysql.db'),
    'raise_on_warnings': True,
    'use_pure': False,
    'autocommit': True,
    'pool_name': 'writerpool',
    'pool_size': 5
}

readonly_connection_config_dict = {
    'user': get_config_val('databases.mysql.username'),
    'password': get_config_val('databases.mysql.password'),
    'host': get_config_val('databases.mysql.read_replica_host'),
    'database': get_config_val('databases.mysql.db'),
    'raise_on_warnings': True,
    'use_pure': False,
    'autocommit': True,
    'pool_name': 'readonlypool',
    'pool_size': 5
}


def __append_to_sql_log(log_type, sql_type, statement, details=""):
    return
    # TODO: temporarily bypassing
    if statement is None:
        statement = ""

    try:
        __cnx = mysql.connector.connect(**writer_connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        sql = """
            INSERT INTO 
                sql_log (
                    log_type, 
                    sql_type, 
                    statement, 
                    details
                )
            VALUES (%s, %s, %s, %s)
        """
        vals = (log_type, sql_type, statement, details)
        __cursor.execute(sql, vals)
        __cnx.commit()

        return __cursor.lastrowid

    except Exception as err:
        log_generic(
            type=c.ERROR,
            sql=sql,
            vals=vals,
            function=whoami(),
            error=err
        )
        return None

    finally:
        if __cnx.is_connected():
            __cursor.close()
            __cnx.close()


def exec_insert(sql, val):
    try:
        __cnx = mysql.connector.connect(**writer_connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        __cursor.execute(sql, val)
        __cnx.commit()

        __append_to_sql_log(
            c.INFO, 'INSERT', __cursor.statement, __cursor.lastrowid)
        return __cursor.lastrowid

    except Error as err:
        __append_to_sql_log(
            c.ERROR,
            'INSERT',
            "{} / {}".format(sql, val),
            err
        )
        return None

    finally:
        if __cnx.is_connected():
            __cursor.close()
            __cnx.close()


def exec_batch_execute(sql, data):
    try:
        __cnx = mysql.connector.connect(**writer_connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        __cursor.executemany(sql, data)
        __cnx.commit()

        return True

    except Error as err:
        __append_to_sql_log(
            c.ERROR,
            'EXECUTE MANY',
            "{}".format(sql),
            err
        )
        print(c.ERROR, 'EXECUTE MANY', "{}".format(sql), err)
        return False

    finally:
        if __cnx.is_connected():
            __cursor.close()
            __cnx.close()


def exec_update(sql, val=()):
    try:
        __cnx = mysql.connector.connect(**writer_connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        __cursor.execute(sql, val)
        __cnx.commit()
        #__append_to_sql_log(c.INFO, 'UPDATE', __cursor.statement, __cursor.rowcount)
        return True if __cursor.rowcount > 0 else False

    except mysql.connector.Error as err:
        __append_to_sql_log(
            c.ERROR,
            'UPDATE',
            __cursor._executed,
            err
        )
        return None

    finally:
        if __cnx.is_connected():
            __cursor.close()
            __cnx.close()


def exec_delete(sql, val=()):
    try:
        __cnx = mysql.connector.connect(**writer_connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        __cursor.execute(sql, val)
        __cnx.commit()
        __append_to_sql_log(
            c.INFO,
            'DELETE',
            __cursor.statement,
            __cursor.rowcount
        )
        return True if __cursor.rowcount > 0 else False

    except mysql.connector.Error as err:
        log_generic(
            type=c.ERROR,
            sql=sql,
            val=val,
            function=whoami(),
            error=err,
            executed=__cursor._executed
        )
        return None

    finally:
        if __cnx.is_connected():
            __cursor.close()
            __cnx.close()


def read_row(sql, val):
    try:
        __cnx = mysql.connector.connect(**writer_connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        __cursor.execute(sql, val)
        __append_to_sql_log(
            c.INFO,
            'SELECT',
            __cursor.statement,
            __cursor.rowcount
        )

        return __cursor.fetchone()

    except mysql.connector.Error as err:
        log_generic(
            type=c.ERROR,
            sql=sql,
            val=val,
            function=whoami(),
            error=err,
            executed=__cursor._executed
        )
        return None

    finally:
        if __cnx and __cnx.is_connected():
            __cursor.close()
            __cnx.close()


def read_rows(sql, vals=None):
    try:
        __cnx = mysql.connector.connect(**writer_connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)
        if vals is None:
            __cursor.execute(sql)
        else:
            __cursor.execute(sql, vals)
        #__append_to_sql_log(INFO, 'SELECT', __cursor.statement, __cursor.rowcount)

        return __cursor.fetchall()

    except mysql.connector.Error as err:
        log_generic(
            type=c.ERROR,
            sql=sql,
            vals=vals,
            function=whoami(),
            error=err,
            executed=__cursor._executed
        )
        return None

    finally:
        if __cnx.is_connected():
            __cursor.close()
            __cnx.close()


def replica_read_row(sql, val):
    try:
        __cnx_ro = mysql.connector.connect(**readonly_connection_config_dict)
        __cursor_ro = __cnx_ro.cursor(dictionary=True, buffered=True)

        __cursor_ro.execute(sql, val)
        __append_to_sql_log(
            c.INFO,
            'SELECT',
            __cursor_ro.statement,
            __cursor_ro.rowcount
        )

        return __cursor_ro.fetchone()

    except mysql.connector.Error as err:
        __append_to_sql_log(
            c.ERROR,
            'SELECT',
            __cursor_ro._executed,
            err
        )
        return None

    finally:
        if (__cnx_ro.is_connected()):
            __cursor_ro.close()
            __cnx_ro.close()


def replica_read_rows(sql, vals=None):
    try:
        __cnx_ro = mysql.connector.connect(**readonly_connection_config_dict)
        __cursor_ro = __cnx_ro.cursor(dictionary=True, buffered=True)
        if vals is None:
            __cursor_ro.execute(sql)
        else:
            __cursor_ro.execute(sql, vals)
        #__append_to_sql_log(INFO, 'SELECT', __cursor.statement, __cursor.rowcount)

        return __cursor_ro.fetchall()

    except mysql.connector.Error as err:
        log_generic(
            type=c.ERROR,
            sql=sql,
            vals=vals,
            function=whoami(),
            error=err,
            executed=__cursor_ro._executed
        )
        return None

    finally:
        if (__cnx_ro.is_connected()):
            __cursor_ro.close()
            __cnx_ro.close()


def exec_sp(stored_procedure: str):
    try:
        __cnx = mysql.connector.connect(**writer_connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        __cursor.callproc(stored_procedure)

        return True

    except mysql.connector.Error as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err,
            executed=__cursor._executed
        )

    finally:
        if __cnx.is_connected():
            __cursor.close()
            __cnx.close()

    return False


'''
except mysql.connector.Error as err:
    __append_to_sql_log(
        c.ERROR,
        'SELECT',
        __cursor._executed, err
    )
    return None
'''
