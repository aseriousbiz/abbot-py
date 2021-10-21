import os
import json
import logging
from .urls import get_skill_api_url
from . import apiclient

class Brain(object):
    """
    Abbot's brain. 

    This has already been instantiated for you in ``bot.brain``.
    """
    def __init__(self, skill_id, user_id, api_token, timestamp):
        self.skill_id = skill_id
        self.request_uri = get_skill_api_url(skill_id) + '/brain?key={0}'
        if self.request_uri.startswith("https://localhost"):
            self.verify_ssl = False
        else:
            self.verify_ssl = True
        self.api_client = apiclient.ApiClient(self.request_uri, user_id, api_token, timestamp)


    def make_uri(self, key):
        return self.request_uri.format(key)


    def get(self, key):
        """
        Get an item from Abbot's brain.

        Args:
            key (str): The item's key.
        
        Returns:
            The string or object stored in Value. This data is JSON serialized.
        """
        uri = self.make_uri(key)
        output = self.api_client.get(uri)
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
        return self.api_client.get(uri)


    def write(self, key, value):
        """
        Write to Abbot's brain. 

        This will overwrite any existing items with the same `key`.

        Args:
            key (str): The lookup key for the object.
            value (object): The string or object to store in Abbot's brain. This data is JSON serialized.
        """
        uri = self.make_uri(key)
        data = {"value": json.dumps(value)}
        return self.api_client.post(uri, data)


    def search(self, term):
        raise NotImplementedError
    

    def delete(self, key):
        """
        Delete an item from Abbot's brain.

        Args:
            key (str): The lookup key for the object to delete.
        """
        uri = self.make_uri(key)
        return self.api_client.delete(uri)


    def test(self, key):
        return "You sent '{}' to the brain.".format(key)
    

    def __str__(self):
        return "Brain for {} skill.".format(self.skill)


    def __repr__(self):
        return "Brain for {} skill.".format(self.skill)