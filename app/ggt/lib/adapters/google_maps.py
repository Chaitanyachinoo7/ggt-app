from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)
import requests


def get_map_thumbnail_url(address):
    gmaps_api_key = get_config_val('google.maps.api_key')
    gmaps_base_url = get_config_val('google.maps.base_url')
    gmaps_map_type = get_config_val('google.maps.map_type')
    gmaps_zoom_level = get_config_val('google.maps.zoom_level')
    gmaps_thumbnail_size = get_config_val('google.maps.thumbnail_size')
    gmaps_markers_color = get_config_val('google.maps.markers_color')
    gmaps_markers_size = get_config_val('google.maps.markers_size')

    map_thumbnail_url = '{}?center={}&zoom={}&size={}&markers={}|{}|{}&maptype={}&key={}'.format(
        gmaps_base_url,
        address,
        gmaps_zoom_level,
        gmaps_thumbnail_size,
        gmaps_markers_color,
        gmaps_markers_size,
        address,
        gmaps_map_type,
        gmaps_api_key
    )
    return map_thumbnail_url


def get_gps_coordinates(addr1, city, st, zip, addr2=None):
    if addr2:
        location_text = "{}+{},{},{}+{}".format(
            addr1,
            addr2,
            city,
            st,
            zip
        )
    else:
        location_text = "{},{},{}+{}".format(
            addr1,
            city,
            st,
            zip
        )

    maps_api_key = get_config_val('google.maps.api_key')
    geocoding_url = get_config_val('google.maps.geo_url') + '?address={}&key={}'.format(location_text,
                                                                                           maps_api_key)
    try:
            r = requests.get(geocoding_url)
            response = r.json()

            lat = response['results'][0]['geometry']['location']['lat']
            lng = response['results'][0]['geometry']['location']['lng']
            return {'lat': lat, 'lng': lng }

    except Exception as err:
            print(err)
            return None
