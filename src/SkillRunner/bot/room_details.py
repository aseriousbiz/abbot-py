from .mention import Mention

# TODO: Is there a Python equivalent to C#'s TimeSpan?

class Threshold(object):
    """
    Represents a warning and deadline threshold.
    """
    def __init__(self, warning: timedelta, deadline: timedelta):
        self.warning = warning
        self.deadline = deadline

    @classmethod
    def from_json(cls, json):
        """
        Returns a Threshold from the JSON payload.
        """
        if json is None:
            return None
        return cls(json.get('Warning'), json.get('Deadline'))


class ResponseSettings(object):
    """
    A set of response settings.
    """
    def __init__(self, response_time, first_responders, escalation_responders):
        self.response_time = response_time
        self.first_responders = first_responders
        self.escalation_responders = escalation_responders

    @classmethod
    def from_json(cls, json):
        """
        Returns a ResponseSettings from the JSON payload.
        """
        if json is None:
            return None
        return cls(
            Threshold.from_json(json.get('ResponseTime')),
            [Mention.from_json(person) for person in json.get('FirstResponders')],
            [Mention.from_json(person) for person in json.get('EscalationResponders')]
        )

class RoomDetails(object):
    """
    Details about a room.
    """
    def __init__(self, id, name, bot_is_member, conversation_tracking_enabled, response_settings, default_response_settings, metadata):
        self.id = id
        self.name = name
        self.bot_is_member = bot_is_member
        self.conversation_tracking_enabled = conversation_tracking_enabled
        self.response_settings = response_settings
        self.default_response_settings = default_response_settings
        self.metadata = metadata

    @classmethod
    def from_json(cls, json):
        """
        Returns a RoomDetails from the JSON payload.
        """
        if json is None:
            return None
        return RoomDetails(
            json.get('Id'),
            json.get('Name'),
            json.get('BotIsMember'),
            json.get('ConversationTrackingEnabled'),
            ResponseSettings.from_json(json.get('ResponseSettings')),
            ResponseSettings.from_json(json.get('DefaultResponseSettings')),
            dict(json.get('Metadata').items())
        )
