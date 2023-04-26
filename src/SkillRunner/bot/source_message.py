from .mention import Mention


class SourceMessage(object):
    """
    The source message for calling a skill. Either the message that invoked the skill
    or the message that was reacted to such as a button click or reaction.
    """

    def __init__(self, id, thread_id, text, url, author):
        self.id = id
        self.thread_id = thread_id
        self.text = text
        self.url = url
        self.author = author

    @classmethod
    def from_json(cls, message_json):
        """
        Returns a SourceMessage from JSON.
        """
        if message_json is None:
            return None
        author = Mention.from_json(message_json.get('Author'))
        return cls(message_json.get('MessageId'), message_json.get('ThreadId'), message_json.get('Text'), message_json.get('MessageUrl'), author)
