import base64
import requests

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id,
    whoami
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    read_rows
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

def task_populate_location_thumbnails():
    print('\n\n********************task_populate_location_thumbnails****************************\n\n')

    sql = """
    SELECT 
        *
    FROM
        locations
    WHERE
        image_thumbnail IS NULL
    """
    rows = read_rows(sql)
    for row in rows:
        location_id = row['id']

        if row['addr2']:
            location_text = "{} {}, {}, {}  {}".format(
                row['addr1'],
                row['addr2'],
                row['city'],
                row['st'],
                row['zip']
            )
        else:
            location_text = "{}, {}, {}  {}".format(
                row['addr1'],
                row['city'],
                row['st'],
                row['zip']
            )

        map_thumbnail_url = 'https://maps.googleapis.com/maps/api/staticmap?center={}&zoom=10&size=110x110&markers=color:red|size:tiny|{}&maptype=roadmap&key=AIzaSyBJmU3ueSBRmXz4mU1MRgdOxAWcfImbQNQ'.format(location_text, location_text)
        encoded_image = base64.b64encode(requests.get(map_thumbnail_url).content)
        update_location_thumbnails(location_id, encoded_image)

    print('\n\n************************************************\n\n')


def update_location_thumbnails(location_id, encoded_image):
    sql = """
        UPDATE 
            locations
        SET
            image_thumbnail = %s,
            update_dt = NOW()
        WHERE 
            id = %s
    """
    vals = (encoded_image, location_id)
    exec_update(sql, vals)    

