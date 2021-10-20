import os
import logging
from .urls import Urls
from . import apiclient

class Secrets(object):
    """
    Abbot's secrets manager. 

    This is automatically instantiated for you as ``bot.secrets``.
    """
    def __init__(self, skill_id, user_id, api_token, timestamp):
        self.skill_id = skill_id
        self.user_id = user_id
        self.request_uri = Urls.get_skill_api_url(skill_id) + '/secret?key={0}'
        if self.request_uri.startswith("https://localhost:4979"):
            logging.warn("AbbotApiBaseUrl appears to be blank. Using localhost as a fallback.")
        self.api_client = apiclient.ApiClient(self.request_uri, user_id, api_token, timestamp)


    def read(self, key):
        """
        Read a secret from the vault. 

        Args: 
            key (str): The key of the secret to retrieve.
        
        Returns: 
            secret (str): The secret from the vault.
        """
        uri = self.request_uri.format(key)
        output = self.api_client.get(uri)
        if output:
            return output.get("secret")
        else:
            return None


    def test(self, key):
        return "You requested a secret called '{}'.".format(key)
    

    def __str__(self):
        return "Secret store for {} skill.".format(self.skill_id)


    def __repr__(self):
        return "Secret store for {} skill.".format(self.skill_id)