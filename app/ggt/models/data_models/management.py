import ggt.lib.constants as c
from ggt.lib.adapters.auth0_config import META_KEY, ORGANIZATION_KEY
from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows
)
from ggt.lib.utils import (
    log_generic,
    whoami
)


########################################################################################################
# [Public] functions
########################################################################################################


def create_new_organisation_request(req):
    try:
        sql = """INSERT INTO organisation_requests
                                  (
                                  org_name,
                                  name,
                                  email,
                                  given_name,
                                  family_name,
                                  nick_name,
                                  status)
                                  VALUES
                                  (%s, %s, %s, %s, %s, %s, %s);
                                  """
        vals = (
            req.org_name,
            req.name,
            req.email,
            req.given_name,
            req.family_name,
            req.nickname,
            'pending'
        )
        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def create_new_organisation(req, ext_id):
    try:
        sql = """INSERT INTO organisations
                                  (id,
                                  name,
                                  email,
                                  owner_ext_id)
                                  VALUES
                                  (%s, %s, %s, %s);
                                  """
        vals = (
            req['id'],
            req['org_name'],
            req['email'],
            ext_id
        )
        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def create_new_user(req, roles):
    try:
        sql = """INSERT IGNORE INTO ggt_users
            (
            email,
            email_verified,
            family_name,
            given_name,
            name,
            picture,
            external_id,
            org_id,
            roles
            )    
            VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s); """
        vals = (
            req['email'],
            req['email_verified'],
            req['family_name'],
            req['given_name'],
            req['name'],
            req['picture'],
            req['user_id'],
            req['user_metadata']['organization'],
            ','.join(roles)
        )
        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def update_user(req):
    try:
        sql = """UPDATE ggt_users
            SET
            email = %s,
            family_name = %s,
            given_name = %s,
            name = %s,
            update_dt = NOW()  
            WHERE 
                external_id = %s """
        vals = (
            req.email,
            req.family_name,
            req.given_name,
            req.name,
            req.ext_id
        )
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def update_user_status(req):
    try:
        sql = """UPDATE ggt_users
            SET
            is_active = %s,
            update_dt = NOW()
            WHERE 
                external_id = %s """
        vals = (
            req.is_active,
            req.ext_id
        )
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def list_org_requests(req):
    try:
        where_statement = "1=1"
        if req.status != '':
            where_statement = "{} AND o.status = '{}'".format(where_statement, req.status)
        sql = """SELECT 
                    o.id as org_id,
                    o.org_name as org_name,
                    o.email as org_email,
                    o.given_name as org_given_name,
                    o.family_name as org_family_name,
                    o.status as org_status,
                    o.comments,
                    o.create_dt as org_create_dt,
                    o.update_dt as org_update_dt,
                    u.external_id,
                    u.email as ggt_user_email,
                    u.family_name,
                    u.given_name
                    
                FROM
                    organisation_requests o
                        LEFT JOIN
                    ggt_users u ON o.resolved_by = u.external_id
                    WHERE
                    {}""".format(where_statement)
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def get_org_request_user(id):
    try:
        sql = """SELECT * FROM organisation_requests
                    WHERE
                    id = %s"""
        vals = (id,)
        return read_row(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def process_org_request(req, user):
    try:

        sql = """UPDATE organisation_requests
                    SET
                    status = %s,
                    comments = %s,
                    resolved_by = %s
                    WHERE
                    id = %s"""
        vals = (req.status, req.comment, user['sub'], req.id)
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def update_user_role(id, roles):
    try:

        sql = """UPDATE ggt_users
                    SET
                    roles = %s
                    WHERE
                    external_id = %s"""
        vals = (','.join(roles), id)
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def delete_user(user_id):
    try:

        sql = """DELETE FROM ggt_users
                    WHERE
                    external_id = %s"""
        vals = (user_id,)
        return exec_delete(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def get_user_by_ext_id(user_id):
    try:
        sql = """SELECT * FROM ggt_users
                    WHERE
                    external_id = %s"""
        vals = (user_id,)
        return read_row(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def list_user(req, user):
    try:

        if user is None:
            return None
        organization_id = user[META_KEY][ORGANIZATION_KEY] if user[META_KEY] else None
        if organization_id is None:
            return None
        where_statement = "org_id = {}".format(organization_id)
        if req.role != "":
            where_statement = "{} AND roles LIKE '%{}%'".format(where_statement, req.role)
        if req.name != "":
            where_statement = "{} AND name LIKE '%{}%'".format(where_statement, req.name)
        if req.email != "":
            where_statement = "{} AND email LIKE '%{}%'".format(where_statement, req.email)
        sql = """SELECT * FROM ggt_users
                    WHERE
                    {}""".format(where_statement)
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def list_organizations(req, user):
    try:
        where_statement = "1=1"
        if req.name != "":
            where_statement = "{} AND o.name LIKE '%{}%'".format(where_statement, req.name)
        sql = """SELECT 
                    o.id AS org_id,
                    o.name AS org_name,
                    o.is_active AS org_active,
                    u.id AS user_id,
                    u.external_id,
                    u.is_active AS user_active,
                    u.email,
                    u.given_name,
                    u.family_name,
                    u.roles,
                    u.picture
                FROM
                    organisations o
                        JOIN
                    ggt_users u ON o.owner_ext_id = u.external_id
                    WHERE
                    {}""".format(where_statement)
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)


def change_org_status(req, user):
    try:
        sql = """UPDATE organisations
                    SET
                    is_active = %s,
                    update_dt = NOW()
                    WHERE id = %s"""
        vals = (req.is_active, req.id)
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err)

