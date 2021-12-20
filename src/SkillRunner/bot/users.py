from .mention import UserMessageTarget

class Users(object):
    def __init__(self):
        pass

    def get_target(self, user_id: str) -> UserMessageTarget:
        """
        Gets a chat address, suitable for sending to with `to`, for a user, given it's platform-specific ID (for example, the User ID 'Unnnnnnn' in Slack).

        This method does not confirm that the user exists.
        If the user does not exist, sending a message to it will fail silently.

        Args:
            id (str): The platform-specific ID of the user.

        Returns: 
            UserMessageTarget: The user message target.
        """
        return UserMessageTarget(user_id)