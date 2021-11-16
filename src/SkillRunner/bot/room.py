from .platform_type import PlatformType


class Room(object):
    """
    A room is a place where people can chat.

    :var id: The room ID.
    :var name: The room name.
    """
    def __init__(self, room_id, room_name, platform_type=None, topic=None, purpose=None):
        self.id = room_id
        self.name = room_name
        self.cache_key = room_id if room_id else room_name
        self._platform_type = platform_type
        self.topic = topic
        self.purpose = purpose


    @classmethod
    def from_json(cls, room_json, platform_type=None):
        platform_type = platform_type if platform_type else PlatformType(room_json.get('PlatformType'))
        return cls(room_json.get('RoomId'), room_json.get('Room'), platform_type)

    @classmethod
    def from_arg_json(cls, room_json, platform_type=None):
        platform_type = platform_type if platform_type else PlatformType(room_json.get('PlatformType'))
        return cls(room_json.get('Id'), room_json.get('Name'), platform_type)


    @classmethod
    def from_conversation_info(cls, room_json, platform_type=None):
        platform_type = platform_type if platform_type else PlatformType(room_json.get('PlatformType'))
        return cls(
            room_json.get('id'),
            room_json.get('name'),
            platform_type,
            room_json.get('topic').get('Value'),
            room_json.get('purpose').get('Value'))


    def __str__(self):
        return f"<#{self.id}|{self.name}>" if self._platform_type == PlatformType.SLACK \
            else f"<@{self.id}>" if self._platform_type == PlatformType.DISCORD \
            else f"#{self.name}"
