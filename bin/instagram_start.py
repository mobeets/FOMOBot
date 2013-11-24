import os
from instagram.client import InstagramAPI

USER_ID = '228175087'
REDIRECT_URI = 'http://www.jehosafet.com'

CLIENT_ID = os.environ['INSTAGRAM_CLIENT_ID']
CLIENT_SECRET = os.environ['INSTAGRAM_CLIENT_SECRET']
ACCESS_CODE = os.environ['INSTAGRAM_ACCESS_CODE']
ACCESS_TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']

def access_token():
    import subprocess
    import json
    cmd = "curl -F 'client_id={0}' -F 'client_secret={1}' -F 'grant_type=authorization_code' -F 'redirect_uri={2}' -F 'code={3}' https://api.instagram.com/oauth/access_token".format(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, ACCESS_CODE)
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    res = json.loads(out)
    token = res['access_token']
    print token
    return token

def no_auth_handle():
    return InstagramAPI(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

def handle(token=ACCESS_TOKEN):
    if token:
        try:
            return InstagramAPI(access_token=token)
        except:
            pass
    try:
        token = access_token()
        return InstagramAPI(access_token=token)
    except:
        print '**** WARNING: NO INSTAGRAM AUTH ****'
        return no_auth_handle()

class InstagramPhoto(object):
    def __init__(self, client, photo):
        """
        need one for Instagram and for Flickr
        """
        self.photo = photo
        self.url = photo.get_standard_resolution_url()
        self.index = str(photo.id)
        self.user = photo.user.full_name
        self.username = photo.user.username
        self.title = photo.caption.text
        self.dt = photo.created_time
        self.lat = photo.location.point.latitude
        self.lon = photo.location.point.longitude
        self.loc_name = self.find_loc_name(client, photo, self.lat, self.lon)

    def find_loc_name(self, client, photo, lat, lon):
        if photo.location.name:
            return photo.location.name
        else:
            try:
                loc = locations_near_location(client, lat, lon)
            except:
                return ''

def locations_near_location(client, lat, lon, dist=None):
    if client is None:
        client = handle()
    if dist:
        return client.location_search(lat=lat, lng=lon, distance=dist)
    else:
        return client.location_search(lat=lat, lng=lon)

def next_photo_at_location(client, lat, lon, pred=None):
    if client is None:
        client = handle()
    if pred is None:
        pred = lambda p: True # defaults to returning first photo
    locs = locations_near_location(client, lat, lon)
    if not locs:
        print 'No Instagram locations near {0}, {1}'.format(lat, lon)
        return
    loc_id = locs[0].id
    recent_media, next = client.location_recent_media(location_id=loc_id)
    for photo in recent_media:
        p = InstagramPhoto(client, photo)
        if pred(p):
            return p

def next_photo_with_location(client=None, pred=None):
    if client is None:
        client = handle()
    if pred is None:
        pred = lambda p: True # defaults to returning first photo
    recent_media, next = client.user_media_feed()
    for media in recent_media:
        if hasattr(media, 'location'):
            p = InstagramPhoto(media)
            if pred(p):
                return p

if __name__ == '__main__':
    access_token()
