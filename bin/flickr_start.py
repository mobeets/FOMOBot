import os
import flickrapi
from datetime import datetime, timedelta

"""
NOTE: using twitter locations from tweets for anything other than tweets violates twitter's ToS
NOTE: Instagram ToS says nothing about caching locations! # http://instagram.com/about/legal/terms/api/

Instagram locations # http://instagram.com/developer/endpoints/locations/
Facebook locations # https://developers.facebook.com/docs/reference/api/user/#posts

I could let people tweet @FOMOBot with their Instagram username, or friend FOMOBot on facebook,
    to grant FOMOBot the ability to use his/her locations in the future?
"""

API_KEY = os.environ['FLICKR_API_KEY']

DEFAULT_LAT = '30.34076'
DEFAULT_LON = '-97.55695'
DEFAULT_RADIUS = 5 # in km, max of 32
DEFAULT_CONTENT_TYPE = 1 # photos only, not screenshots
DEFAULT_ACCURACY = 11 # city-level

flickr_dt_str = lambda dt: dt.strftime('%Y-%m-%d')


def handle():
    return flickrapi.FlickrAPI(API_KEY)

def photo_url(photo, size='medium'):
    """
    source: http://www.flickr.com/services/api/misc.urls.html

    size_id_map
        s   small square 75x75
        t   thumbnail, 100 on longest side
        m   small, 240 on longest side
        z   medium 640, 640 on longest side
        b   large, 1024 on longest side
    """
    farm = photo.get('farm')
    server = photo.get('server')
    photo_id = photo.get('id')
    secret = photo.get('secret')
    base = 'http://farm{farm_id}.staticflickr.com/{server_id}/{id}_{secret}_{size_id}.jpg'
    size_id_map = {'small': 'm', 'small square': 's', 'thumbnail': 't', 'medium': 'z', 'large': 'b'}
    return base.format(farm_id=farm, server_id=server, id=photo_id, secret=secret, size_id=size_id_map[size])

class FlickrPhoto(object):
    def __init__(self, photo):
        """
        need one for Instagram and for Flickr
        """
        self.photo = photo
        self.url = photo_url(photo)
        self.index = str(photo.get('id'))
        self.user = photo.get('owner')
        self.title = photo.get('title')

def next_photo_at_location(api, lat, lon, pred=None, radius=DEFAULT_RADIUS):
    """
    source: http://www.flickr.com/services/api/flickr.photos.search.html

    returns first photo in search results s.t. pred(photo) is True
    """
    if api is None:
        api = handle()
    if pred is None:
        pred = lambda p: True # defaults to returning first photo
    for photo in api.walk(
            lat=lat,
            lon=lon,
            radius=radius,
            accuracy=DEFAULT_ACCURACY,
            # content_type=DEFAULT_CONTENT_TYPE,
            # media='photos',
            min_taken_date=flickr_dt_str(datetime.now() - timedelta(days=365)),
            max_taken_date=flickr_dt_str(datetime.now())):
        p = FlickrPhoto(photo)
        if pred(p):
            # photo['url'] = photo_url(photo)
            return p
    return None

if __name__ == '__main__':
    tmp = next_photo_at_location(handle(), DEFAULT_LAT, DEFAULT_LON)
    print '-------'
    print tmpa
