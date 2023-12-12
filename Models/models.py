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
