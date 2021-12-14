
from SkillRunner.bot.mention import UserConversation


class Users(object):
    def __init__(self):
        pass

    def get_conversation(self, user_id: str) -> UserConversation:
        """
        Gets a user conversation given it's platform-specific ID (for example, the User ID 'Unnnnnnn' in Slack).

        This method does not confirm that the user exists.
        If the user does not exist, sending a message to it will fail silently.

        Args:
            id (str): The platform-specific ID of the user.

        Returns: 
            UserConversation: The user conversation.
        """
        return UserConversation(user_id)