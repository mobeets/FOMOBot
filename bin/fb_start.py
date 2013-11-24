import os
import facebook

APP_TOKEN = os.environ['FACEBOOK_APP_TOKEN']
USER_TOKEN = os.environ['FACEBOOK_USER_TOKEN']

# API: https://github.com/pythonforfacebook/facebook-sdk

# http://blog.carduner.net/2010/05/26/authenticating-with-facebook-on-the-command-line-using-python/
# https://developers.facebook.com/tools/access_token/

def handle():
    return facebook.GraphAPI(USER_TOKEN)

def next_post_with_location(graph=None, pred=None):
    if graph is None:
        graph = handle()
    if pred is None:
        pred = lambda post: True # defaults to returning first post

    feed = graph.get_connections("me", "home", **{'with': 'location'})
    # feed['paging']
    for post in feed['data']: # these are already sorted by most recent to least recent
        if pred(post):
            return post
        # loc = post['place']
        # [u'city', u'zip', u'country', u'longitude', u'state', u'street', u'latitude']
        # loc_name = loc['name']
        # loc_lat = loc['location']['latitude']
        # loc_lon = loc['location']['longitude']

if __name__ == '__main__':
    next_post_with_location()
