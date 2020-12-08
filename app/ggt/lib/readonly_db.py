from ggt.lib.adapters.readonly_mysql_adapter import (
    read_row as __read_row,
    read_rows as __read_rows
)


async def read_row(sql, val):
    return __read_row(sql, val)


async def read_rows(sql, vals=None):
    return __read_rows(sql, vals)
