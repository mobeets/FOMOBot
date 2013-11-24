import os
from twython import Twython
from dateutil import parser

# https://dev.twitter.com/apps/4784263/show
CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
OAUTH_TOKEN = os.environ['TWITTER_OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['TWITTER_OAUTH_TOKEN_SECRET']

TWEET_LENGTH = 140
TWEET_URL_LENGTH = 21

def user_handle():
    return Twython(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

def follower_ids(handle=None):
    if not handle:
        handle = user_handle()
    """
    only the first page!
    """
    ids = handle.get_followers_ids()
    return ids['ids']

def following_ids(handle=None):
    if not handle:
        handle = user_handle()
    ids = handle.get_friends_ids()
    return ids['ids']

def sync_followers_and_followings(handle=None):
    if not handle:
        handle = user_handle()
    followers = set(follower_ids(handle))
    followings = set(following_ids(handle))
    need_to_follow = list(followers - followings)
    need_to_unfollow = list(followings - followers)
    for i in need_to_follow:
        print 'Following user #{0}'.format(i)
        handle.create_friendship(user_id=i, follow=True)
    for i in need_to_unfollow:
        print 'Unfollowing user #{0}'.format(i)
        handle.destroy_friendship(user_id=i)

def location_name_guess(handle, lat, lon):
    res = handle.reverse_geocode(lat=lat, long=lon)
    if 'result' not in res:
        return ''
    if 'places' not in res['result']:
        return ''
    locs = res['result']['places']
    if not locs:
        return ''
    return locs[0]['full_name']

class Tweet(object):
    def __init__(self, status):
        """
        need one for Instagram and for Flickr

        NOTE: indices are cast to str since they are sometimes too big
        """
        self.status = status
        self.index = str(status['id'])
        self.user = status['user']['name']
        self.username = status['user']['screen_name']
        self.user_id = str(status['user']['id'])
        self.dt = parser.parse(status['created_at'])
        self.loc_name, self.lat, self.lon = self.location_details(status)
        self.is_retweet = 'retweeted_status' in status

    def location_details(self, status):
        loc_name = None
        lat = None
        lon = None
        if status['coordinates']:
            lon = status['coordinates']['coordinates'][0]
            lat = status['coordinates']['coordinates'][1]
        if status['place']:
            loc_name = status['place']['full_name']
        if loc_name and not lat:
            lon, lat = status['place']['bounding_box']['coordinates'][0][0]
        return loc_name, lat, lon

def post_status(handle, content, tweet_reply_id=None):
    if not handle:
        handle = user_handle()
    handle.update_status(status=content, in_reply_to_status_id=tweet_reply_id)

def next_tweet_with_location(handle, user_ids_to_ignore, tweet_ids_to_ignore):
    if not handle:
        handle = user_handle()
    timeline = handle.get_home_timeline()
    for status in timeline:
        t = Tweet(status)
        if not t.is_retweet and t.lat and t.user_id not in user_ids_to_ignore and t.index not in tweet_ids_to_ignore:
            if not t.loc_name:
                t.loc_name = location_name_guess(t.lat, t.lon)
            return t
