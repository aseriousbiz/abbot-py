import os
import json
import requests
import logging

from . import apiclient

class Brain(object):
    """
    Abbot's brain. 

    This has already been instantiated for you in ``bot.brain``.
    """
    def __init__(self, skill_id, user_id, api_token, timestamp):
        self.skill_id = skill_id
        self.request_uri = os.environ.get('SkillApiBaseUriFormatString', 'https://localhost:4979/api/skills/{0}') + '/brain?key={1}'
        if self.request_uri.startswith("https://localhost"):
            self.verify_ssl = False
        else:
            self.verify_ssl = True
        self.api_client = apiclient.ApiClient(self.request_uri, user_id, api_token, timestamp)


    def make_uri(self, key):
        return self.request_uri.format(self.skill_id, key)


    def get(self, key):
        """
        Get an item from Abbot's brain.

        Args:
            key (str): The item's key.
        
        Returns:
            The string or object stored in Value.
        """
        uri = self.make_uri(key)
        output = self.api_client.get(uri)
        if output:
            return output.get("value")
        else:
            return None
    

    def read(self, key):
        """
        See `get`.
        """
        value = self.get(key)
        if value:
            return json.loads(self.get(key))
        return value

    
    def list(self):
        uri = self.make_uri("")
        return self.api_client.get(uri)


    def write(self, key, value):
        """
        Write to Abbot's brain. 

        This will overwrite any existing items with the same `key`.

        Args:
            key (str): The lookup key for the object.
            value (object): The string or object to store in Abbot's brain.
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