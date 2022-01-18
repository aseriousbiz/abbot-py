from .chat_address import ChatAddress, ChatAddressType
from .platform_type import PlatformType

class RoomMessageTarget(object):
    """
    A room message target is a handle that can be used to send messages to that room.

    :var id: The room ID.
    """
    def __init__(self, room_id):
        self.id = room_id

    def get_chat_address(self):
        return ChatAddress(ChatAddressType.ROOM, self.id)

    def get_thread(self, thread_id: str):
        """
        Gets a handle to the specified thread in this room.

        Args:
            thread_id (str): The platform-specific thread ID.
        """
        return ChatAddress(ChatAddressType.ROOM, self.id, thread_id)

class Room(RoomMessageTarget):
    """
    A room is a place where people can chat.

    :var id: The room ID.
    :var name: The room name.
    """
    def __init__(self, room_id, room_name, platform_type=None, topic=None, purpose=None):
        super().__init__(room_id)
        self.name = room_name
        self.cache_key = room_id if room_id else room_name
        self._platform_type = platform_type
        self.topic = topic
        self.purpose = purpose

    def __eq__(self, other):
        return isinstance(other, Room) and \
            self.id == other.id and \
            self.name == other.name and \
            self.cache_key == other.cache_key and \
            self._platform_type == other._platform_type and \
            self.topic == other.topic and \
            self.purpose == other.purpose


    @classmethod
    @classmethod
    def from_json(cls, room_json, platform_type=None):
        room = room_json.get('Room')
        if isinstance(room, dict):
            cls.from_arg_json(room)
        else:
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
