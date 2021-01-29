import os
import json
import requests
import logging

from __app__.SkillRunner.apiclient import ApiClient

class Utilities(object):
    def __init__(self, skill_id, user_id, api_token, timestamp):
        self.skill_id = skill_id
        self.request_uri = os.environ.get('SkillApiBaseUriFormatString', 'https://localhost:4979/api/skills/{0}') 
        if self.request_uri.startswith("https://localhost"):
            self.verify_ssl = False
        else:
            self.verify_ssl = True
        self.api_client = ApiClient(self.request_uri, user_id, api_token, timestamp)


    def make_uri(self, key):
        return self.request_uri.format(self.skill_id, key)

    
    def geocode(self, address, include_timezone=False):
        clean_address = requests.utils.requote_uri(address)
        uri = self.request_uri + "/geo?address={}&includeTimezone={}".format(clean_address, include_timezone)
        result = self.api_client.get(uri)

        # This will return an object that contains a string called Address, and an (int, int) tuple called Geocode 
        # representing the lat/lng of the point.
        return result


    def __str__(self):
        return "Utilities object for {} skill.".format(self.skill)


    def __repr__(self):
        return "Utilities object for {} skill.".format(self.skill)