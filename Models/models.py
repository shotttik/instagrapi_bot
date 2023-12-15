import config


class UserShort:
    def __init__(self, pk, username, full_name, *args, **kwargs):
        self.pk = pk
        self.username = username
        self.full_name = full_name

    def to_dict(self):
        return {
            "pk": self.pk,
            "username": self.username,
            "full_name": self.full_name
        }


class HttpUrl:
    def __init__(self, link, *args, **kwargs) -> None:
        self.link = link


class UserInfo:
    def __init__(self, user_data):
        self.id = user_data.get('pk')
        self.username = user_data.get('username')
        self.full_name = user_data.get('full_name')
        self.is_private = user_data.get('is_private')
        self.profile_pic_url = user_data.get('profile_pic_url')
        self.is_verified = user_data.get('is_verified')
        self.media_count = user_data.get('media_count')
        self.follower_count = user_data.get('follower_count')
        self.following_count = user_data.get('following_count')
        self.biography = user_data.get('biography')
        self.external_url = user_data.get('external_url')
        self.is_business = user_data.get('is_business')

    @property
    def row_string(self) -> str:
        return f"{self.id};{self.username};{self.full_name};{self.is_private};{self.profile_pic_url};{self.is_verified};{self.media_count};{self.follower_count};{self.following_count};{self.biography};{self.external_url};{self.is_business};{config.TYPE}\n"

    @property
    @staticmethod
    def row_header_string() -> str:
        return "id;username;full_name;is_private;profile_pic_url;is_verified;media_count;follower_count;following_count;biography;external_url;is_business;TYPE"
