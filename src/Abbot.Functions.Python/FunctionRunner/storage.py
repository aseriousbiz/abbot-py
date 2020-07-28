import os
import requests
import hmac
import hashlib
import logging

class Brain(object):
    def __init__(self, skill_id, user_id, api_token):
        self.skill_id = skill_id
        self.user_id = user_id
        self.request_uri = os.environ.get('UserSkillApiUriFormatString', 'https://localhost:4979/api/skill/{0}/data/{1}')
        self.request_header = {
                'Content-Type': 'application/json',
                'X-Abbot-SkillApiToken': api_token, 
                'X-Abbot-PlatformUserId': str(user_id)
            }

    def make_uri(self, key):
        return self.request_uri.format(self.skill_id, key)

    def read(self, key):
        uri = self.make_uri(key)
        response = requests.get(uri, headers=self.request_header)
        if response.status_code == 200:
            output = response.json()
            return output.get("value")
        else:
            return response.json()

    def write(self, key, value):
        uri = self.make_uri(key)
        logging.info("URI: " + uri)
        data = {"value": value}
        result = requests.post(uri, headers=self.request_header, json=data)
        if result.status_code == 200:
            logging.info(result.json())
            return result.json()
        else:
            logging.info(result.reason)
            logging.info(dir(result))
            raise Exception

    def search(self, term):
        raise NotImplementedError
    
    def list(self):
        raise NotImplementedError
    
    def delete(self, key):
        uri = self.make_uri(key)
        return requests.delete(uri, headers=self.request_header)

    def test(self, key):
        return "You sent '{}' to the brain.".format(key)
    
    def __str__(self):
        return "Brain for {} skill.".format(self.skill)

    def __repr__(self):
        return "Brain for {} skill.".format(self.skill)