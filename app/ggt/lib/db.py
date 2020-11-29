from ggt.lib.adapters.mysql_adapter import (
    exec_insert as __exec_insert,
    exec_update as __exec_update,
    exec_delete as __exec_delete,
    read_row as __read_row,
    read_rows as __read_rows,
    exec_batch_execute as __exec_batch_execute
)

'''
def passthrough(*args, **kwargs):
    return target(*args, **kwargs)
'''

def exec_insert(sql, val):
    return __exec_insert(sql, val)


def exec_update(sql, val=()):
    return __exec_update(sql, val)


def exec_delete(sql, val=()):
    return __exec_delete(sql, val)


def read_row(sql, val):
    return __read_row(sql, val)


def read_rows(sql, vals=None):
    return __read_rows(sql, vals)


def exec_batch_execute(sql, data):
    return __exec_batch_execute(sql, data)
