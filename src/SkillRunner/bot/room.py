import logging
from .platform_type import PlatformType


class Room(object):
    """
    A room is a place where people can chat.

    :var id: The room ID.
    :var name: The room name.
    """
    def __init__(self, room_id, room_name, platform_type):
        self.id = room_id
        self.name = room_name
        self.cache_key = room_id if room_id else room_name
        self._platform_type = platform_type
        logging.error(platform_type)


    @classmethod
    def from_json(cls, room_json):
        return cls(room_json.get('RoomId'), room_json.get('Room'), PlatformType(room_json.get('PlatformType')))


    def __str__(self):
        return f"<#{self.id}|{self.name}>" if self._platform_type == PlatformType.SLACK else f"<@{self.id}>" if self._platform_type == PlatformType.DISCORD else self.name
