import json
import urllib.parse

class Brain(object):
    """
    Abbot's brain. 

    This has already been instantiated for you in ``bot.brain``.
    """
    def __init__(self, api_client):
        self._api_client = api_client

    def __get_path(self, key):
        return f"/brain?key={urllib.parse.quote_plus(key)}"

    def get(self, key):
        """
        Get an item from Abbot's brain.

        Args:
            key (str): The item's key.
        
        Returns:
            The string or object stored in Value. This data is JSON serialized.
        """
        path = self.__get_path(key)
        try:
            output = self._api_client.get(path)
            if output:
                return json.loads(output.get("value"))
            else:
                return None
        except Exception:
            return None

    def read(self, key):
        """
        See `get`.
        """
        return self.get(key)

    def list(self):
        path = self.__get_path("")
        return self._api_client.get(path)

    def write(self, key, value):
        """
        Write to Abbot's brain. 

        This will overwrite any existing items with the same `key`.

        Args:
            key (str): The lookup key for the object.
            value (object): The string or object to store in Abbot's brain. This data is JSON serialized.
        """
        path = self.__get_path(key)
        data = {"value": json.dumps(value)}
        return self._api_client.post(path, data)

    def search(self, term):
        raise NotImplementedError

    def delete(self, key):
        """
        Delete an item from Abbot's brain.

        Args:
            key (str): The lookup key for the object to delete.
        """
        path = self.__get_path(key)
        return self._api_client.delete(path)

    def __str__(self):
        return "Brain for the skill."

    def __repr__(self):
        return "Brain for the skill."