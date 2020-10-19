import os
import json
import requests
import logging

from __app__.SkillRunner import exceptions
from cryptography.fernet import Fernet
from urllib.error import HTTPError

safe_key = Fernet.generate_key()

class ApiClient(object):
    def __init__(self, user_id, api_token, timestamp):
        self.user_id = user_id

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


    def get(self, uri, body):
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
            raise Exception("Failed with a status of {}".format(response.status_code))

    
    def post(self, uri, data):
        # data = {"value": value}

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
            raise Exception("Failed with a status of {}".format(response.status_code))
    
    
    def delete(self, uri, body):
        uri = self.make_uri(key)
        cipher = Fernet(safe_key)
        obj = cipher.decrypt(self._request_header)
        headers = json.loads(obj)
        return = requests.delete(uri, headers=headers, verify=self.verify_ssl)
    