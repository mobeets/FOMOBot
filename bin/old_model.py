import pickle
DBFILE = 'out.pickle'

class Data(object):
    def __init__(self, clear_first=False, dbfile=DBFILE):
        self.dbfile = dbfile
        if clear_first:
            self.clear()
        self.data = self.load()
        self.tweet_user_ids = self.data['tweet_user_ids']
        self.tweet_ids = self.data['tweet_ids']
        self.used_flickr_ids = self.data['used_flickr_ids']
        self.used_insta_ids = self.data['used_insta_ids']

    def load(self):
        if not os.path.exists(self.dbfile):
            return {}
        with open(self.dbfile, 'rb') as f:
            return pickle.load(f)

    def clear(self):
        data = {
            'tweet_ids': [],
            'tweet_user_ids': [],
            'used_flickr_ids': [],
            'used_insta_ids': []
        }
        with open(self.dbfile, 'wb') as f:
            pickle.dump(data, f)

    def save(self):
        with open(self.dbfile, 'wb') as f:
            pickle.dump(self.data, f)
