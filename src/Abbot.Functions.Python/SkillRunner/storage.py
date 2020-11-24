import os
import json
import requests
import logging

from __app__.SkillRunner.apiclient import ApiClient

class Brain(object):
    def __init__(self, skill_id, user_id, api_token, timestamp):
        self.skill_id = skill_id
        self.request_uri = os.environ.get('SkillApiBaseUriFormatString', 'https://localhost:4979/api/skills/{0}') + '/data/{1}'
        if self.request_uri.startswith("https://localhost"):
            self.verify_ssl = False
        else:
            self.verify_ssl = True
        self.api_client = ApiClient(self.request_uri, user_id, api_token, timestamp)


    def make_uri(self, key):
        return self.request_uri.format(self.skill_id, key)


    def get(self, key):
        uri = self.make_uri(key)
        output = self.api_client.get(uri)
        if output:
            return output.get("value")
        else:
            return None
    

    def read(self, key):
        return self.get(key)

    
    def list(self):
        uri = self.make_uri("")
        return self.api_client.get(uri)


    def write(self, key, value):
        uri = self.make_uri(key)
        data = {"value": value}
        return self.api_client.post(uri, data)


    def search(self, term):
        raise NotImplementedError
    

    def delete(self, key):
        uri = self.make_uri(key)
        return self.api_client.delete(uri)


    def test(self, key):
        return "You sent '{}' to the brain.".format(key)
    

    def __str__(self):
        return "Brain for {} skill.".format(self.skill)


    def __repr__(self):
        return "Brain for {} skill.".format(self.skill)