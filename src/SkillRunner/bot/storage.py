import json
import urllib.parse

class Brain(object):
    """
    Abbot's brain. 

    This has already been instantiated for you in ``bot.brain``.
    """
    def __init__(self, api_client):
        self._api_client = api_client


    def __make_uri(self, key):
        return f"/brain?key={urllib.parse.quote_plus(key)}"


    def get(self, key):
        """
        Get an item from Abbot's brain.

        Args:
            key (str): The item's key.
        
        Returns:
            The string or object stored in Value. This data is JSON serialized.
        """
        uri = self.__make_uri(key)
        output = self._api_client.get(uri)
        if output:
            return json.loads(output.get("value"))
        else:
            return None
    

    def read(self, key):
        """
        See `get`.
        """
        return self.get(key)


    def list(self):
        uri = self.make_uri("")
        return self._api_client.get(uri)


    def write(self, key, value):
        """
        Write to Abbot's brain. 

        This will overwrite any existing items with the same `key`.

        Args:
            key (str): The lookup key for the object.
            value (object): The string or object to store in Abbot's brain. This data is JSON serialized.
        """
        uri = self.__make_uri(key)
        data = {"value": json.dumps(value)}
        return self._api_client.post(uri, data)


    def search(self, term):
        raise NotImplementedError
    

    def delete(self, key):
        """
        Delete an item from Abbot's brain.

        Args:
            key (str): The lookup key for the object to delete.
        """
        uri = self.__make_uri(key)
        return self._api_client.delete(uri)


    def __str__(self):
        return "Brain for the skill."


    def __repr__(self):
        return "Brain for the skill."