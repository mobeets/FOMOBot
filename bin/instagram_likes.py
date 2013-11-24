from instagram_start import handle

h = handle()

def user_max_likes(username):
    user_id = h.user_search(username)[0].id
    recent_media, next = h.user_recent_media(user_id=user_id)

    max_lc = 0
    max_url = None
    for media in recent_media:
        lc = media.like_count
        if lc > max_lc:
            max_lc = lc
            max_url = media.link
    return max_lc, max_url

def main():
    import sys
    username = sys.argv[1]
    print user_max_likes(username)

if __name__ == '__main__':
    main()