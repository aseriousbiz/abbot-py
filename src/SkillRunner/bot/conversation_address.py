from enum import IntEnum
from typing import Optional

class ConversationType(IntEnum):
    USER = 0
    ROOM = 1

class ConversationAddress(object):
    def __init__(self, type: ConversationType, id: str, thread_id: Optional[str] = None):
        self.type = type
        self.id = id
        self.thread_id = thread_id
    
    def get_conversation_address(self):
        return self

    def __eq__(self, other):
        return self.type == other.type and self.id == other.id and self.thread_id == other.thread_id

    def __repr__(self) -> str:
        if self.thread_id is None:
            return f"{self.type.name}:{self.id}"
        else:
            return f"{self.type.name}/{self.id}({self.thread_id})"
    
    def toJSON(self):
        ret = {
            "Type": self.type.value,
            "Id": self.id,
        }
        if self.thread_id is not None:
            ret["ThreadId"] = self.thread_id
        return ret