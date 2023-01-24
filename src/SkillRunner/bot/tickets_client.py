from .api_result import ApiResult

class TicketsClient(object):
    """
    Used to reply with a message to open a ticket.
    """
    def __init__(self, api_client, bot):
        self._api_client = api_client
        self._bot = bot

    def reply_with_ticket_prompt():
        """
        Replies with an ephemeral message that displays a button to open a ticket for
        each enabled ticketing system.
        """
        body = {
            "User": self._bot.from_user.id,
            "MessageId": self._bot.message_id,
            "ConversationIdentifier": {
                "Channel": self._bot.room.id,
                "MessageId": self._bot.thread.thread_id or self._bot.message_id,
                "ConversationId": self._bot.conversation.id,
            }
        }

        return ApiResult(self._api_client.post('/ticket/buttons', body))