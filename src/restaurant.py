from json import dumps


class Restaurant:
    def __init__(self, blurhash, launch_date, location, name, online, popularity):
        self.blurhash = blurhash
        self.launch_date = launch_date
        self.location = location
        self.launch_date = launch_date
        self.name = name
        self.online = online
        self.popularity = popularity

        self.launched_days = None
        self.distance = None

    def as_response_dict(self):
        response_dict = self.__dict__.copy()
        response_dict.pop("distance")
        response_dict.pop("launched_days")

        return response_dict
