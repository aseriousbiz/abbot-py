import os
import logging
import requests


class Secrets(object):
    def __init__(self, skill_id, user_id, api_token, timestamp):
        self.skill_id = skill_id
        self.user_id = user_id
        uri_base = os.environ.get('UserSkillApiUriFormatString', 'https://localhost:4979/api/skill/{0}/data/{1}')
        self.request_uri = uri_base.replace('/data/', '/secret/')
        self._request_header = {
                'Content-Type': 'application/json',
                'X-Abbot-SkillApiToken': api_token, 
                'X-Abbot-PlatformUserId': str(user_id),
                'X-Abbot-Timestamp': str(timestamp)
            }

    @property
    def request_header(self):
        return None

    @request_header.setter
    def request_header(self, value):
        self._request_header = value

    def make_uri(self, key):
        return self.request_uri.format(self.skill_id, key)

    def read(self, key):
        uri = self.make_uri(key)
        response = requests.get(uri, headers=self._request_header)
        if response.status_code == 200:
            output = response.json()
            return output.get("secret")
        elif response.status_code == 404:
            return None
        else:
            return "Failed with a status of {}".format(response.status_code)
    
    def test(self, key):
        return "You requested a secret called '{}'.".format(key)
    
    def __str__(self):
        return "Secret store for {} skill.".format(self.skill_id)

    def __repr__(self):
        return "Secret store for {} skill.".format(self.skill_id)