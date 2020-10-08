import mysql.connector
from mysql.connector import Error

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

connection_config_dict = {
    'user': get_config_val('databases.mysql.username'),
    'password': get_config_val('databases.mysql.password'),
    'host': get_config_val('databases.mysql.host'),
    'database': get_config_val('databases.mysql.db'),
    'raise_on_warnings': True,
    'use_pure': False,
    'autocommit': True,
    'pool_name': 'mypool',
    'pool_size': 5
}


def __append_to_sql_log(log_type, sql_type, statement, details=""):
    return
    # TODO: temporarily bypassing
    if statement is None:
        statement = ""

    try:
        __cnx = mysql.connector.connect(**connection_config_dict)
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
            type=ERROR,
            sql=sql,
            vals=vals,
            function=whoami(),
            error=err)
        return None

    finally:
        if (__cnx.is_connected()):
            __cursor.close()
            __cnx.close()


def exec_insert(sql, val):
    try:
        __cnx = mysql.connector.connect(**connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        __cursor.execute(sql, val)
        __cnx.commit()

        __append_to_sql_log(
            INFO, 'INSERT', __cursor.statement, __cursor.lastrowid)
        return __cursor.lastrowid

    except Error as err:
        __append_to_sql_log(
            ERROR,
            'INSERT',
            "{} / {}".format(sql, val),
            err
        )
        return None

    finally:
        if (__cnx.is_connected()):
            __cursor.close()
            __cnx.close()


def exec_batch_execute(sql, data):
    try:
        __cnx = mysql.connector.connect(**connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        __cursor.executemany(sql, data)
        __cnx.commit()

        return True

    except Error as err:
        __append_to_sql_log(
            ERROR,
            'EXECUTE MANY',
            "{}".format(sql),
            err
        )
        print(ERROR, 'EXECUTE MANY', "{}".format(sql), err)
        return False

    finally:
        if (__cnx.is_connected()):
            __cursor.close()
            __cnx.close()


def exec_update(sql, val=()):
    try:
        __cnx = mysql.connector.connect(**connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        __cursor.execute(sql, val)
        __cnx.commit()
        #__append_to_sql_log(INFO, 'UPDATE', __cursor.statement, __cursor.rowcount)
        return True if __cursor.rowcount > 0 else False

    except mysql.connector.Error as err:
        __append_to_sql_log(
            ERROR,
            'UPDATE',
            __cursor._executed,
            err
        )
        return None

    finally:
        if (__cnx.is_connected()):
            __cursor.close()
            __cnx.close()


def exec_delete(sql, val):
    try:
        __cnx = mysql.connector.connect(**connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        __cursor.execute(sql, val)
        __cnx.commit()
        __append_to_sql_log(
            INFO,
            'DELETE',
            __cursor.statement,
            __cursor.rowcount
        )
        return True if __cursor.rowcount > 0 else False

    except mysql.connector.Error as err:
        __append_to_sql_log(
            ERROR,
            'DELETE',
            __cursor._executed,
            err
        )
        return None

    finally:
        if (__cnx.is_connected()):
            __cursor.close()
            __cnx.close()


def read_row(sql, val):
    try:
        __cnx = mysql.connector.connect(**connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        __cursor.execute(sql, val)
        __append_to_sql_log(
            INFO,
            'SELECT',
            __cursor.statement,
            __cursor.rowcount
        )
        return __cursor.fetchone()

    except mysql.connector.Error as err:
        __append_to_sql_log(
            ERROR,
            'SELECT',
            __cursor._executed,
            err
        )
        return None

    finally:
        if (__cnx.is_connected()):
            __cursor.close()
            __cnx.close()


def read_rows(sql, vals=None):
    try:
        __cnx = mysql.connector.connect(**connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)
        if vals is None:
            __cursor.execute(sql)
        else:
            __cursor.execute(sql, vals)
        #__append_to_sql_log(INFO, 'SELECT', __cursor.statement, __cursor.rowcount)
        return __cursor.fetchall()

    except mysql.connector.Error as err:
        __append_to_sql_log(
            ERROR,
            'SELECT',
            __cursor._executed, err
        )
        return None

    finally:
        if (__cnx.is_connected()):
            __cursor.close()
            __cnx.close()
