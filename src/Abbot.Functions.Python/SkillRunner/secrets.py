import os
import logging
import requests
import json

from cryptography.fernet import Fernet
from __app__.SkillRunner.apiclient import ApiClient

safe_key = Fernet.generate_key()

class Secrets(object):
    def __init__(self, skill_id, user_id, api_token, timestamp):
        self.skill_id = skill_id
        self.user_id = user_id
        uri_base = os.environ.get('UserSkillApiUriFormatString', 'https://localhost:4979/api/skill/{0}/data/{1}')
        self.request_uri = uri_base.replace('/data/', '/secret/')
        self.api_client = ApiClient(self.request_uri, user_id, api_token, timestamp)


    def read(self, key):
        uri = self.request_uri.format(self.skill_id, key)
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