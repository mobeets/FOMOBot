from sqlalchemy import Column, Integer, String
from db_connect import Base

INSTAGRAM_PHOTO = 0
FLICKR_PHOTO = 1
KINDS = [INSTAGRAM_PHOTO, FLICKR_PHOTO]

class InstagramPhoto(Base):
    __tablename__ = 'instagram_photos'
    id = Column(Integer, primary_key=True)
    media_id = Column(String)
    url = Column(String)

class FlickrPhoto(Base):
    __tablename__ = 'flickr_photos'
    id = Column(Integer, primary_key=True)
    media_id = Column(String)
    url = Column(String)

class Tweet(Base):
    __tablename__ = 'tweets'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    media_id = Column(String)
    msg = Column(String)

class Data(object):
    def __init__(self, db):
        db.create_if_not_exists([Tweet, FlickrPhoto, InstagramPhoto])
        self.db_session = db.session()

    def used_photos(self, kind):
        assert kind in KINDS
        if kind == INSTAGRAM_PHOTO:
            cls = InstagramPhoto
        else:
            cls = FlickrPhoto
        ids = []
        for inst in self.db_session.query(cls).order_by(cls.id):
            ids.append(inst.media_id)
        return ids

    def used_tweets(self):
        cls = Tweet
        user_ids = []
        tweet_ids = []
        for inst in self.db_session.query(cls).order_by(cls.id):
            user_ids.append(inst.user_id)
            tweet_ids.append(inst.media_id)
        return user_ids, tweet_ids

    def add_photo(self, kind, photo):
        assert kind in KINDS
        if kind == INSTAGRAM_PHOTO:
            obj = InstagramPhoto(media_id=photo.index, url=photo.url)
        else:
            obj = FlickrPhoto(media_id=photo.index, url=photo.url)
        self.db_session.add(obj)
        self.db_session.commit()

    def add_tweet(self, tweet, msg):
        obj = Tweet(user_id=tweet.user_id, media_id=tweet.index, msg=msg)
        self.db_session.add(obj)
        self.db_session.commit()
