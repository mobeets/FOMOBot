import os
import time
from random import choice

from bin.db_connect import Engine
from bin.flickr_start import next_photo_at_location as flickr_photo
from bin.instagram_start import next_photo_at_location as insta_photo
from bin.model import Data, INSTAGRAM_PHOTO, FLICKR_PHOTO
from bin.claims import get_post
from bin.next_location import location, bounding_box
from bin.twitter_streamer import TWEET_URL_LENGTH, TWEET_LENGTH, user_handle, next_tweet_at_location, post_status, sync_followers_and_followings

LOCS_FILE = 'bin/locs.csv'
LOC_POPS_FILE = 'bin/loc_pops.csv'

TWEET_EVERY_N_SECONDS = 60*10 # e.g. 60*10 = ten minutes between each tweet

def get_photo(lat, lon, used_flickr_ids, used_insta_ids):
    def insta():
        pred = lambda photo: photo.index not in used_flickr_ids
        return flickr_photo(None, lat, lon, pred)
    def flick():
        pred = lambda photo: photo.index not in used_insta_ids
        return insta_photo(None, lat, lon, pred)
    status = FLICKR_PHOTO
    if True:
        status = INSTAGRAM_PHOTO
        p = insta()
        if not p:
            status = FLICKR_PHOTO
            p = flick()
    else:
        p = flick()
        if not p:
            status = INSTAGRAM_PHOTO
            p = insta()
    return p, status

def tweet_is_okay_length(text):
    no_url = ' '.join([x for x in text.split() if 'http' not in x])
    if (len(no_url) + TWEET_URL_LENGTH) > TWEET_LENGTH:
        return False
    return True

def msg(msgs, out):
    print '+++++++++++++' + str(out)
    msgs.append(out)

def msg_close(msgs):
    return '<br>'.join(msgs)

def old_tweet_bot(db):
    """
    http://www.easycron.com/user
    """
    out = []

    data = Data(db)
    twitter_handle = user_handle()
    msg(out, 'Updating friendships...')
    sync_followers_and_followings(twitter_handle)

    msg(out, 'Fetching data...')
    tweet_user_ids, tweet_ids = data.used_tweets()
    used_flickr_ids = data.used_photos(FLICKR_PHOTO)
    used_insta_ids = data.used_photos(INSTAGRAM_PHOTO)
    
    # find first tweet with location from user who follows you whose id is not in tweet ids read
    # and whose user has not been mentioned in last post
    msg(out, 'Finding next tweet...')
    tweet = next_tweet_with_location(twitter_handle, tweet_user_ids[-1:], tweet_ids)
    if not tweet:
        msg(out, 'ERROR: No tweets found.')
        return msg_close(out)

    # find next photo at location whose photo_id has not been used yet
    photo, status = get_photo(tweet.lat, tweet.lon, used_flickr_ids, used_insta_ids)
    if not photo:
        msg(out, 'ERROR: No photos found near {0}, {1}'.format(tweet.lat, tweet.lon))
    if not tweet.loc_name and status == INSTAGRAM_PHOTO:
        msg(outm, 'Using Instagram location name')
        tweet.loc_name = photo.loc_name

    text = get_post(tweet.username, tweet.loc_name, photo.url)
    msg(out, 'Created tweet "{0}" in reply to tweet #{1}'.format(text, tweet.index))
    if not tweet_is_okay_length(text):
        msg(out, 'ERROR: Tweet is too long!')
        return msg_close(out)

    post_status(twitter_handle, text, tweet.index)
    
    # updating data
    data.add_tweet(tweet, text)
    msg(out, 'Chose photo from...')
    if INSTAGRAM_PHOTO:
        msg(out, 'instagram')
        data.add_photo(INSTAGRAM_PHOTO, photo)
    else:
        msg(out, 'flickr')
        data.add_photo(FLICKR_PHOTO, photo)

    return msg_close(out)

# def tweet_bot(db, datadir='.'):
def tweet_bot(datadir='.'):
    out = []

    msg(out, 'Fetching data...')
    # data = Data(db)
    # tweet_user_ids, tweet_ids = data.used_tweets()
    # used_flickr_ids = data.used_photos(FLICKR_PHOTO)
    # used_insta_ids = data.used_photos(INSTAGRAM_PHOTO)
    
    tweet_user_ids = []
    used_flickr_ids = []
    used_insta_ids = []

    loc = location(os.path.join(datadir, LOCS_FILE), os.path.join(datadir, LOC_POPS_FILE))
    while not loc:
        loc = location(os.path.join(datadir, LOCS_FILE), os.path.join(datadir, LOC_POPS_FILE))
    msg(out, 'Choosing location: {0}, {1}'.format(loc.city, loc.region))
    loc_name = loc.city
    lat, lon = loc.latitude, loc.longitude
    geos = bounding_box(loc)

    # find next photo at location whose photo_id has not been used yet
    photo, status = get_photo(lat, lon, used_flickr_ids, used_insta_ids)
    if not photo:
        msg(out, 'ERROR: No photos found near {0}, {1}'.format(loc.city, loc.region))
        return msg_close(out)
    sta = 'Chose photo from...'
    if INSTAGRAM_PHOTO:
        sta += 'instagram'
    else:
        sta += 'flickr'
    msg(out, sta)

    msg(out, 'Waiting for next tweet...')
    tweet, success = next_tweet_at_location(loc, geos, tweet_user_ids)
    if not success:
        msg(out, 'ERROR: No tweets found: {0}'.format(tweet))
        return msg_close(out)

    text = get_post(tweet.username, loc_name, photo.url)
    msg(out, 'Tweeting: {0}'.format(text))
    if not tweet_is_okay_length(text):
        msg(out, 'ERROR: Tweet is too long!')
        return msg_close(out)

    twitter_handle = user_handle()
    sync_followers_and_followings(twitter_handle)
    post_status(twitter_handle, text, tweet.index)
    
    # # updating data
    # data.add_tweet(tweet, text)
    # if INSTAGRAM_PHOTO:
    #     data.add_photo(INSTAGRAM_PHOTO, photo)
    # else:
    #     data.add_photo(FLICKR_PHOTO, photo)

    return msg_close(out)

def main():
    # db = Engine()
    CURDIR = os.path.dirname(os.path.abspath(__file__))
    while True:
        print tweet_bot(CURDIR)
        # print tweet_bot(db, CURDIR)
        time.sleep(TWEET_EVERY_N_SECONDS)

if __name__ == '__main__':
    main()
