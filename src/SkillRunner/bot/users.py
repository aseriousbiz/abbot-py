import urllib.parse

from .mention import UserMessageTarget, UserProfile
from .apiclient import ApiClient

class Users(object):
    """
    Users API client
    """

    _api_client: ApiClient

    def __init__(self, api_client: ApiClient):
        self._api_client = api_client

    def get_target(self, user_id: str) -> UserMessageTarget:
        """
        Gets a chat address, suitable for sending to with `to`, for a user, given it's platform-specific ID (for example, the User ID 'Unnnnnnn' in Slack).

        This method does not confirm that the user exists.
        If the user does not exist, sending a message to it will fail silently.

        Args:
            user_id (str): The platform-specific ID of the user.

        Returns: 
            UserMessageTarget: The user message target.
        """
        return UserMessageTarget(user_id)
    
    def get_user(self, user_id: str) -> UserProfile:
        """
        Gets a user's profile, given their platform-specific ID (for example, the User ID 'Unnnnnnn' in Slack).

        Args:
            user_id (str): The platform-specific ID of the user.

        Returns: 
            UserProfile: The user profile.
        """
        response = self._api_client.get(f"/users/{urllib.parse.quote_plus(user_id)}")
        return UserProfile.from_json(response)