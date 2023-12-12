import sys
from common import find_full_user_data_from_list_of_shorts, get_limited_media_likers
from config import POSTS_SORT


def search_media_by_hashtag(cl) -> list:
    if POSTS_SORT == "top":
        medias = cl.hashtag_medias_top('downhill', amount=2)
    elif POSTS_SORT == "recent":
        medias = medias = cl.hashtag_medias_recent('downhill', amount=2)
    else:
        print("POSTS_SSORT Invalid value! please fix and re-run the script...")
        sys.exit()

    media_likers = get_limited_media_likers(medias, cl)
    full_data_of_media_likers = find_full_user_data_from_list_of_shorts(
        media_likers, cl)
    return full_data_of_media_likers

    # save
    # data to google sheets
