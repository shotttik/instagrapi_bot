import sys
from common import get_limited_media_likers
from config import POSTS_SORT, TARGET


def search_media_by_hashtag(cl) -> list:
    if POSTS_SORT == "top":
        medias = cl.hashtag_medias_top(TARGET, amount=2)
    elif POSTS_SORT == "recent":
        medias = medias = cl.hashtag_medias_recent(TARGET, amount=2)
    else:
        print("POSTS_SORT Invalid value! please fix and re-run the script...")
        sys.exit()

    media_likers = get_limited_media_likers(medias, cl)

    return media_likers

    # save
    # data to google sheets
