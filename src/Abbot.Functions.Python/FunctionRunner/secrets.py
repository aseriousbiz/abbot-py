import os
import logging
import requests
import json
from cryptography.fernet import Fernet

safe_key = Fernet.generate_key()

class Secrets(object):
    def __init__(self, skill_id, user_id, api_token, timestamp):
        self.skill_id = skill_id
        self.user_id = user_id
        uri_base = os.environ.get('UserSkillApiUriFormatString', 'https://localhost:4979/api/skill/{0}/data/{1}')
        self.request_uri = uri_base.replace('/data/', '/secret/')
         
        header_obj = {
                'Content-Type': 'application/json',
                'X-Abbot-SkillApiToken': api_token, 
                'X-Abbot-PlatformUserId': str(user_id),
                'X-Abbot-Timestamp': str(timestamp)
            }
        
        # In order to prevent users from accessing sensitive data, we encrypt it using Fernet, 
        # then decrypt in the accessors. 
        obj = json.dumps(header_obj).encode('utf-8')
        cipher = Fernet(safe_key)
        self._request_header = cipher.encrypt(obj)

    def make_uri(self, key):
        return self.request_uri.format(self.skill_id, key)

    def read(self, key):
        uri = self.make_uri(key)
        cipher = Fernet(safe_key)
        obj = cipher.decrypt(self._request_header)
        req_header = json.loads(obj)

        response = requests.get(uri, headers=req_header)
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