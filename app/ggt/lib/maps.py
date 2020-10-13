from ggt.lib.adapters.google_maps import (
    get_map_thumbnail_url as __get_google_maps_thumbnail_url
)

def get_map_thumbnail_url(address):
    return __get_google_maps_thumbnail_url(address)
