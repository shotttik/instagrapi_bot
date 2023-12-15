from common import get_limited_media_likers
from config import POSTS_SORT, TARGET
import sys


def search_media_by_location(cl) -> list:
    # Search Location by GEO coordinates
    loc = cl.location_search(*TARGET)[0]

    # Complete blank fields
    loc = cl.location_complete(loc)

    location_dict = loc.dict()
    location_id = location_dict["pk"]
    location_name = location_dict["name"]
    if POSTS_SORT == "top":
        medias = cl.location_medias_top(location_id, amount=2)
    elif POSTS_SORT == "recent":
        medias = cl.location_medias_recent(location_id, amount=2)
    else:
        print("POSTS_SSORT Invalid value! please fix and re-run the script...")
        sys.exit()

    media_likers = get_limited_media_likers(medias, cl)

    return (media_likers, location_name)
