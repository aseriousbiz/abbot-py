class MessageOptions(object):
    """
    Creates a message options object from the provided keyword arguments.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def toJSON(self):
        """
        Returns a dictionary suitable for sending to the Reply API
        """
        ret = {}

        # 'to', if present, should be an object that has a conversation address
        to = self.__dict__.get('to')
        if to is not None and hasattr(to, 'get_conversation_address') and callable(to.get_conversation_address):
            ret['to'] = to.get_conversation_address().toJSON()

        return ret
