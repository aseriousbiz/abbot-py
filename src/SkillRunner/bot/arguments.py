import logging
import jsonpickle
from collections import MutableSequence
from .mention import Mention
from .room import Room

class Argument(object):
    """
    An argument parsed from the bot.arguments property. Arguments may be delimited by a space or 
    by a matching pair of quotes.

    :var value: The normalized argument value
    :var original_text: The original argument value. For quoted values this would include the surrounding quotes.
    """
    def __init__(self, value, original_text):
        self.value = value
        self.original_text = original_text


    def __repr__(self):
        return self.value


    def __str__(self):
        return self.value


    @staticmethod
    def load_argument(arg_json, platform_type=None):
        logging.info(f"arg_json: {jsonpickle.encode(arg_json)}")
        value = arg_json.get('Value')
        original_text = arg_json.get('OriginalText')
        mentioned_arg = arg_json.get('Mentioned')
        room_arg = arg_json.get('Room')
        mentioned = Mention.from_json(mentioned_arg, platform_type)
        return MentionArgument(value, original_text, mentioned) if mentioned \
            else RoomArgument(value, original_text, Room.from_json(room_arg, platform_type)) if room_arg \
            else Argument(value, original_text)


class MentionArgument(Argument):
    """
    An argument that represents a mentioned user.
    """
    def __init__(self, value, original_text, mentioned):
        super().__init__(value, original_text)
        self.mentioned = mentioned

    def __str__(self):
        return "mentioned: {}".format(self.mentioned)


class RoomArgument(Argument):
    """
    An argument that is a room mention (for example `#room-name` in Slack).
    """
    def __init__(self, value, original_text, room):
        super().__init__(value, original_text)
        self.room = room


    def __str__(self):
        return str(self.room)
