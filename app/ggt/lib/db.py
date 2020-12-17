from ggt.lib.adapters.mysql_adapter import (
    exec_insert as __exec_insert,
    exec_update as __exec_update,
    exec_delete as __exec_delete,
    read_row as __read_row,
    read_rows as __read_rows,
    replica_read_row as __replica_read_row,
    replica_read_rows as __replica_read_rows,
    exec_batch_execute as __exec_batch_execute,
    exec_sp as __exec_sp
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


def read_row(sql, vals=()):
    return __read_row(sql, vals)


def read_rows(sql, vals=None):
    return __read_rows(sql, vals)


def exec_batch_execute(sql, data):
    return __exec_batch_execute(sql, data)


def exec_sp(stored_procedure):
    return __exec_sp(stored_procedure)


def replica_read_row(sql, vals=()):
    return __replica_read_row(sql, vals)


def replica_read_rows(sql, vals=None):
    return __replica_read_rows(sql, vals)
