import os
import json
import requests
import logging

from cryptography.fernet import Fernet

safe_key = Fernet.generate_key()

class Brain(object):
    def __init__(self, skill_id, user_id, api_token, timestamp):
        self.skill_id = skill_id
        self.user_id = user_id
        self.request_uri = os.environ.get('UserSkillApiUriFormatString', 'https://localhost:4979/api/skill/{0}/data/{1}')
        if self.request_uri.startswith("https://localhost"):
            self.verify_ssl = False
        else:
            self.verify_ssl = True

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
        headers = json.loads(obj)

        response = requests.get(uri, headers=headers, verify=self.verify_ssl)
        if response.status_code == 200:
            output = response.json()
            return output.get("value")
        elif response.status_code == 404:
            return None
        else:
            return "Failed with a status of {}".format(response.status_code)

    
    def list(self):
        uri = self.make_uri("")
        logging.info("Getting list with this URL: " + uri)
        cipher = Fernet(safe_key)
        obj = cipher.decrypt(self._request_header)
        headers = json.loads(obj)

        response = requests.get(uri, headers=headers, verify=self.verify_ssl)
        if response.status_code == 200:
            output = response.json()
            return output
        elif response.status_code == 404:
            return None
        else:
            return "Failed with a status of {}".format(response.status_code)


    def write(self, key, value):
        uri = self.make_uri(key)
        data = {"value": value}

        cipher = Fernet(safe_key)
        obj = cipher.decrypt(self._request_header)
        headers = json.loads(obj)

        result = requests.post(uri, headers=headers, verify=self.verify_ssl, json=data)
        if result.status_code == 200:
            return result.json()
        else:
            logging.info("Couldn't write to the brain. ")
            logging.info("Got Status Code: " + str(result.status_code))
            logging.info(result.json())
            raise Exception


    def search(self, term):
        raise NotImplementedError
    

    def delete(self, key):
        uri = self.make_uri(key)
        cipher = Fernet(safe_key)
        obj = cipher.decrypt(self._request_header)
        headers = json.loads(obj)
        return requests.delete(uri, headers=headers, verify=self.verify_ssl)


    def test(self, key):
        return "You sent '{}' to the brain.".format(key)
    

    def __str__(self):
        return "Brain for {} skill.".format(self.skill)


    def __repr__(self):
        return "Brain for {} skill.".format(self.skill)