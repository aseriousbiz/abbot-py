from .mention import Mention

# TODO: Is there a Python equivalent to C#'s TimeSpan?

class Threshold(object):
    def __init__(self, warning, deadline):
        self.warning = warning
        self.deadline = deadline

    @classmethod
    def from_json(cls, json):
        if json is None:
            return None
        return cls(json.get('Warning'), json.get('Deadline'))


class ResponseSettings(object):
    def __init__(self, response_time, first_responders, escalation_responders):
        self.response_time = response_time
        self.first_responders = first_responders
        self.escalation_responders = escalation_responders

    @classmethod
    def from_json(cls, json):
        if json is None:
            return None
        return cls(
            Threshold.from_json(json.get('ResponseTime')),
            [Mention.from_json(person) for person in json.get('FirstResponders')],
            [Mention.from_json(person) for person in json.get('EscalationResponders')]
        )

class RoomDetails(object):
    def __init__(self, id, name, botIsMember, conversationTrackingEnabled, responseSettings, defaultResponseSettings, metadata):
        self.id = id
        self.name = name
        self.botIsMember = botIsMember
        self.conversationTrackingEnabled = conversationTrackingEnabled
        self.responseSettings = responseSettings
        self.defaultResponseSettings = defaultResponseSettings
        self.metadata = metadata

    @classmethod
    def from_json(cls, json):
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
