from ggt.lib.utils import (
    log_generic
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows
)


########################################################################################################
# [Public] functions
########################################################################################################
def get_all_printer_hubs():
    try:
        sql = "SELECT * FROM workstations"
        return read_rows(sql)

    except Exception as err:
        log_generic(type="error", function='get_all_printer_hubs', error=err)
        return None


def create_print_job(workstation_id, appointment_id):
    if __enqueue(workstation_id, appointment_id):
        return True

    return False


def get_next_print_job(workstation_id, workstation_token):
    next_print_job = __peek(workstation_id, workstation_token)
    if next_print_job:
        __dequeue(next_print_job['id'])


########################################################################################################
# [Protected] functions
########################################################################################################

def __enqueue(workstation_id, appointment_id):
    try:
        sql = """
                INSERT INTO label_print_queue 
                    (workstation_id, appointment_id) 
                VALUES 
                    (%s, %s)
            """
        vals = (workstation_id, appointment_id)
        return exec_insert(sql, vals)

    except Exception as err:
        log_generic(type="error", function='printers.__enqueue', error=err)
        return None


def __dequeue(print_job_id):
    try:
        sql = """
                UPDATE 
                    label_print_queue 
                SET 
                    dequeue_dt = NOW(), 
                    status = 'printed' 
                WHERE 
                    id = %s
            """
        vals = (print_job_id,)
        return exec_update(sql, vals)

    except Exception as err:
        log_generic(type="error", function='printers.__dequeue', error=err)
        return None


def __peek(workstation_id, workstation_token):
    try:
        sql = """
                SELECT 
                    q.id,
                    a.id AS appointment_id,
                    p.first_name,
                    p.middle_name
                    p.last_name,
                    p.dob,
                    a.scheduled_dt
                FROM
                    label_print_queue q
                        INNER JOIN
                    workstations w ON q.workstation_id = w.id
                        INNER JOIN
                    appointments a ON q.appointment_id = a.id
                        INNER JOIN
                    patients p ON p.id = a.patient_id
                WHERE 1 
                    AND w.id = %s
                    AND w.token = %s
                    AND q.status = 'pending'
                LIMIT 1
            """
        vals = (workstation_id, workstation_token)
        return read_row(sql, vals)

    except Exception as err:
        log_generic(type="error", function='printers.__peek', error=err)
        return None
