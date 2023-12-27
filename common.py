import sys

from emoji import demojize
from config import LIMIT, MIN_FOLLOWERS, MAX_FOLLOWERS


def get_limited_media_likers(medias: list, cl):
    if len(medias) < 1:
        print("Couldn't find medias.")
        sys.exit()

    media_data = medias[0].dict()
    media_id = media_data["pk"]

    media_likers = cl.media_likers(media_id)
    return media_likers[:LIMIT]  # Limiting users


def find_full_user_data_from_list_of_shorts(media_likers: list, cl):
    full_data_list = []
    for media_liker in media_likers:
        user_full_data = cl.user_info_by_username(
            media_liker.username).dict()
        followers_count = user_full_data["followers_count"]
        if followers_count > MIN_FOLLOWERS and followers_count < MAX_FOLLOWERS:
            full_data_list.append(user_full_data)
    return full_data_list
