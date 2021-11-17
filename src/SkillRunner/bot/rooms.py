import logging
import jsonpickle
import urllib.parse
from .room import Room

class Rooms(object):
    """
    Abbot's rooms client. Used to manage Slack conversations.

    This is automatically instantiated for you as ``bot.rooms``.
    """
    def __init__(self, api_client, platform_type):
        self._api_client = api_client
        self._platform_type = platform_type

    def create(self, name, is_private=False):
        """
        Creates a Room and returns a Result that indicates whether the operation succeeded or not, 
        and contains information about the created room if it was success.

        Args: 
            name (str): The name of the room.
            is_private (bool): Whether the room is private or not.

        Returns: 
            result (Result): indicates whether the operation succeeded or not and contains information about the created room.
        """
        response = self._api_client.put(f"/rooms", {"name": name, "is_private": is_private})
        if (response.get('ok')):
            return Result(response.get("channel"), self._platform_type)
        else:
            return Result(response.get("error"))

    def archive(self, room):
        """
        Archives a Room and returns a result if it succeeded.

        Args:
            room (Room): The room to archive.

        Returns: 
            result (Result): indicates whether the operation succeeded or not and contains information about the created room.
        """
        url = f"{self.__room_url(room)}/archive"
        response = self._api_client.put(url)
        if (response.get('ok')):
            return Result(None)
        else:
            return Result(response.get("error"))

    def invite_users(self, room, users):
        """
        Invites users to a Room and returns a result if it succeeded.

        Args:
            room (Room): The room to invite the users to.
            users (list): The users to invite.

        Returns: 
            result (Result): indicates whether the operation succeeded or not and contains information about the created room.
        """
        url = self.__room_url(room)
        user_ids = [user.id for user in users]
        response = self._api_client.post(url, user_ids)
        if (response.get('ok')):
            return Result(None)
        else:
            return Result(response.get("error"))

    def set_topic(self, room, topic):
        """
        Sets the topic for a Room and returns a result if it succeeded.

        Args:
            room (Room): The room to set the topic for.
            topic (str): The topic to set for the room.

        Returns: 
            result (Result): indicates whether the operation succeeded or not and contains information about the created room.
        """
        url = f"{self.__room_url(room)}/topic"
        response = self._api_client.post(url, topic)
        if (response.get('ok')):
            return Result(None)
        else:
            return Result(response.get("error"))

    def set_purpose(self, room, purpose):
        """
        Sets the purpose for a Room and returns a result if it succeeded.

        Args:
            room (Room): The room to set the purpose for.
            topic (str): The purpose to set for the room.

        Returns: 
            result (Result): indicates whether the operation succeeded or not and contains information about the created room.
        """
        url = f"{self.__room_url(room)}/purpose"
        response = self._api_client.post(url, purpose)
        if (response.get('ok')):
            return Result(None)
        else:
            return Result(response.get("error"))

    def __room_url(self, room):
        """
        Returns the URL for a Room.

        Args: 
            room (Room): The room to get the URL for.

        Returns: 
            str: The URL for the room.
        """
        return f"/rooms/{urllib.parse.quote_plus(room.id)}"


class Result(object):
    """
    Represents a result from calling the rooms API.
    """
    def __init__(self, roomOrError, platform_type=None):
        if (isinstance(roomOrError, str)):
            self.ok = False
            self.error = roomOrError    
        else:
            self.ok = True
            self.value = Room.from_conversation_info(roomOrError, platform_type) if roomOrError is not None else None