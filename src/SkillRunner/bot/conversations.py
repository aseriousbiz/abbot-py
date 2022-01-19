from .chat_address import ChatAddress, ChatAddressType
from .mention import Mention
from .room import Room

import json

import dateutil

class Conversation(object):
    def __init__(self, id, first_message_id, title, room, started_by, created, last_message_posted_on, members):
        self.id = id
        self.__first_message_id = first_message_id
        self.title = title
        self.room = room
        self.started_by = started_by
        self.created = created
        self.last_message_posted_on = last_message_posted_on
        self.members = members

    @classmethod
    def from_json(cls, conversation_json, platform_type=None):
        if conversation_json is None:
            return None
        room_arg = conversation_json.get('Room')
        room = Room.from_arg_json(room_arg, platform_type) if room_arg is not None else None

        started_by_arg = conversation_json.get('StartedBy')
        started_by = Mention.from_json(started_by_arg, platform_type) if started_by_arg is not None else None

        created_arg = conversation_json.get('Created')
        created = dateutil.parser.isoparse(created_arg) if created_arg is not None else None
        lmpo_arg = conversation_json.get('LastMessagePostedOn')
        lmpo = dateutil.parser.isoparse(lmpo_arg) if lmpo_arg is not None else None

        members_arg = conversation_json.get('Members')
        members = [
            Mention.from_json(x, platform_type) for x in members_arg
        ] if members_arg is not None else None

        return cls(
            conversation_json.get('Id'),
            conversation_json.get('FirstMessageId'),
            conversation_json.get('Title'),
            room,
            started_by,
            created,
            lmpo,
            members)

    def get_chat_address(self):
        return ChatAddress(ChatAddressType.ROOM, self.room.id, self.__first_message_id)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)