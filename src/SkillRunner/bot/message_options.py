from .chat_address import ChatAddress, ChatAddressType

class MessageOptions(object):
    """
    Creates a message options object from the provided keyword arguments.
    """
    def __init__(self, bot, **kwargs):
        self.bot = bot
        self.__dict__.update(kwargs)

    def toJSON(self):
        """
        Returns a dictionary suitable for sending to the Reply API
        """
        ret = {}

        # 'to', if present, should be an object that has a conversation address
        to = self.__dict__.get('to')
        if to is not None and hasattr(to, 'get_chat_address') and callable(to.get_chat_address):
            ret['to'] = to.get_chat_address().toJSON()

        # 'ephemeral', if present, should be a boolean
        ephemeral = self.__dict__.get('ephemeral')
        if ephemeral is True:
            if to is None:
                to = self.bot.from_user.get_chat_address().id
            else:
                to = to.get_chat_address().id
            ret['to'] = ChatAddress(ChatAddressType.ROOM, self.bot.room.id, ephemeral_user_id=to).toJSON()

        return ret
