from common import find_full_user_data_from_list_of_shorts, get_limited_media_likers
from config import POSTS_SORT, LIMIT, TARGET
import sys
from Models.models import UserShort


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
    # save
    # data to google sheets

# media_likers = [
#     UserShort(pk='6295408642', username='esthersotode', full_name='esther soto de castro', profile_pic_url=HttpUrl(
#         'https://ifbcAQXY&_nc_sid=8809c9', scheme='https',), profile_pic_url_hd=None, is_private=False, stories=[]),
#     UserShort(pk='772213762', username='evidimitrakaki', full_name='Evi Dimitrakaki', profile_pic_url=HttpUrl(
#         'https://iUAXvLmSWO1y7D4_sid=8809c9', scheme='https',), profile_pic_url_hd=None, is_private=True, stories=[]),
#     UserShort(pk='207138050', username='eugenie_yarokhno', full_name='Eugenie Yarokhno', profile_pic_url=HttpUrl(
#         'https://instagra0=voA-5&M=8809c9', scheme='https', ), profile_pic_url_hd=None, is_private=False, stories=[]),
#     UserShort(pk='174313732', username='epickkk_', full_name='Kmmm', profile_pic_url=HttpUrl(
#         'https://innXPNRgY_KJpUQ5w&oe=657AB0D8&_nc_sid=8809c9', scheme='https',), profile_pic_url_hd=None, is_private=True, stories=[]),
#     UserShort(pk='965189381', username='mariannasorriso', full_name='Marianna Sorriso', profile_pic_url=HttpUrl(
#         'h_18991561905530565.fn09c9', scheme='https',), profile_pic_url_hd=None, is_private=True, stories=[])
# ]
