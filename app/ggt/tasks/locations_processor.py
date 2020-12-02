import base64
import requests
import logging

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id,
    whoami
)

from ggt.lib.db import (
    exec_insert,
    exec_update,
    read_rows
)

import ggt.lib.constants as c

#TODO: read the params from Config files

async def task_populate_location_thumbnails():
    print('\n\n********************task_populate_location_thumbnails****************************\n\n')

    sql = """
    SELECT 
        *
    FROM
        locations
    WHERE
        image_thumbnail IS NULL
    """
    rows = await read_rows(sql)
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
        await update_location_thumbnails(location_id, encoded_image)

    print('\n\n************************************************\n\n')


async def update_location_thumbnails(location_id, encoded_image):
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
    await exec_update(sql, vals)    



async def task_populate_gps_coordinates():
    print('\n\n********************task_populate_gps_coordinates****************************\n\n')

    sql = """
    SELECT 
        *
    FROM
        locations
    WHERE
        lat IS NULL OR 
        lng IS NULL OR
        lat = '' OR 
        lng = ''
    """
    
    rows = await read_rows(sql)
    for row in rows:
        location_id = row['id']

        if row['addr2']:
            location_text = "{}+{},{},{}+{}".format(
                row['addr1'],
                row['addr2'],
                row['city'],
                row['st'],
                row['zip']
            )
        else:
            location_text = "{},{},{}+{}".format(
                row['addr1'],
                row['city'],
                row['st'],
                row['zip']
            )

        maps_api_key = 'AIzaSyAf7kDO2y7Hz7HYb3LHqvXimqJQcA6X8DQ'
        geocoding_url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(location_text, maps_api_key)

        try:
            r = requests.get(geocoding_url)
            response = r.json()

            lat = response['results'][0]['geometry']['location']['lat']
            lng = response['results'][0]['geometry']['location']['lng']

            await update_gps_coordinates(location_id, lat, lng)

        except Exception as err:
            print(err)


        

    print('\n\n************************************************\n\n')




async def update_gps_coordinates(location_id, lat, lng):
    sql = """
        UPDATE 
            locations
        SET
            lat = %s,
            lng = %s,
            update_dt = NOW()
        WHERE 
            id = %s
    """
    vals = (lat, lng, location_id)
    await exec_update(sql, vals)    



