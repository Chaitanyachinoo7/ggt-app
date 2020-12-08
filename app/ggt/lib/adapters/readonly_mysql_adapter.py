import mysql.connector
from mysql.connector import Error

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

import ggt.lib.constants as c


connection_config_dict = {
    'user': get_config_val('databases.mysql.username'),
    'password': get_config_val('databases.mysql.password'),
    'host': '35.236.213.48',
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
            type=c.ERROR,
            sql=sql,
            vals=vals,
            function=whoami(),
            error=err
        )
        return None

    finally:
        if (__cnx.is_connected()):
            __cursor.close()
            __cnx.close()



def read_row(sql, vals):
    try:
        '''
        log_generic(
            type=c.INFO,
            sql=sql,
            vals=vals,
            function=whoami()
        )
        '''
        __cnx = mysql.connector.connect(**connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)

        __cursor.execute(sql, val)
        __append_to_sql_log(
            c.INFO,
            'SELECT',
            __cursor.statement,
            __cursor.rowcount
        )
        log_generic(
            type=c.INFO,
            sql=sql,
            vals=vals,
            function=whoami(),
            executed=__cursor._executed
        )

        return __cursor.fetchone()

    except mysql.connector.Error as err:
        __append_to_sql_log(
            c.ERROR,
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
    log_generic(
        type=c.INFO,
        sql=sql,
        vals=vals,
        function=whoami()
    )
    try:
        __cnx = mysql.connector.connect(**connection_config_dict)
        __cursor = __cnx.cursor(dictionary=True, buffered=True)
        if vals is None:
            __cursor.execute(sql)
        else:
            __cursor.execute(sql, vals)
        #__append_to_sql_log(INFO, 'SELECT', __cursor.statement, __cursor.rowcount)
        log_generic(
            type=c.INFO,
            sql=sql,
            vals=vals,
            function=whoami(),
            executed=__cursor._executed
        )

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
        if (__cnx.is_connected()):
            __cursor.close()
            __cnx.close()
