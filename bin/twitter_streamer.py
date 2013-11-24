import os
from twython import Twython
from twython import TwythonStreamer

from dateutil import parser
from unidecode import unidecode

from next_location import location, bounding_box

# https://dev.twitter.com/apps/4784263/show
CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
OAUTH_TOKEN = os.environ['TWITTER_OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['TWITTER_OAUTH_TOKEN_SECRET']

TWEET_LENGTH = 140
TWEET_URL_LENGTH = 21

def user_handle():
    return Twython(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

class Tweet(object):
    def __init__(self, status):
        """
        need one for Instagram and for Flickr

        NOTE: indices are cast to str since they are sometimes too big
        """
        self.status = status
        self.msg = status['text'] if type(status['text']) is str else unidecode(status['text'])
        self.index = str(status['id'])
        self.user = status['user']['name']
        self.username = status['user']['screen_name']
        self.user_id = str(status['user']['id'])
        self.dt = parser.parse(status['created_at'])
        self.is_retweet = 'retweeted_status' in status

    def set_location(self, loc_name, lat, lon):
        self.loc_name = loc_name
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return '{0} says "{1}" from {2}'.format(self.user, self.msg, self.loc_name)

bounding_box_param = lambda geos: ','.join([str(x) for x in geos])
class LocationStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            tweet = Tweet(data)
            if tweet.user_id in self.user_ids_to_ignore:
                return
            self.disconnect()
            tweet.set_location(self.loc.city, self.loc.latitude, self.loc.longitude)
            self.tweet = tweet

    def on_error(self, status_code, data):
        self.tweet_error = data
        print status_code, data
        self.disconnect()

def next_tweet_at_location(loc, geos, user_ids_to_ignore):
    stream = LocationStreamer(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    stream.loc = loc
    stream.user_ids_to_ignore = user_ids_to_ignore
    stream.statuses.filter(locations=bounding_box_param(geos))
    if not hasattr(stream, 'tweet'):
        return stream.tweet_error, False
    return stream.tweet, True

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

def post_status(handle, content, tweet_reply_id=None):
    if not handle:
        handle = user_handle()
    handle.update_status(status=content, in_reply_to_status_id=tweet_reply_id)

if __name__ == '__main__':
    print next_tweet_at_location(None, None, [])
