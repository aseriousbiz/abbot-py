import json
import requests
import logging
import os

from cryptography.fernet import Fernet
from urllib.error import HTTPError

try:
    safe_key = Fernet.generate_key()
except AttributeError:
    # This may be running in a context where Fernet is mocked
    pass

class ApiClient(object):
    """
    Api Client for the skill runner APIs hosted on abbot-web. This class understands the 
    authentication mechanism when calling a skill runner API.
    """
    def __init__(self, skill_id, user_id, api_token, timestamp, trace_parent):
        self.user_id = user_id

        base_url = os.environ.get('AbbotApiBaseUrl', 'https://localhost:4979/api')
        self.base_url = f'{base_url}/skills/{skill_id}'

        if self.base_url.startswith("https://localhost"):
            self.verify_ssl = False
        else:
            self.verify_ssl = True

        header_obj = {
                'Content-Type': 'application/json',
                'X-Abbot-SkillApiToken': api_token, 
                'X-Abbot-PlatformUserId': str(user_id),
                'X-Abbot-Timestamp': str(timestamp),
                'traceparent': trace_parent
            }
        logging.info(f'ApiClient created with traceparent: {trace_parent}')
        
        # In order to prevent users from accessing sensitive data, we encrypt it using Fernet, 
        # then decrypt in the accessors. 
        obj = json.dumps(header_obj).encode('utf-8')
        cipher = Fernet(safe_key)
        self._request_header = cipher.encrypt(obj)


    def get(self, path, body=None):
        """
        Makes a GET request to the Abbot API.
        Arguments:
            path: The path to the resource to GET. This is the part after https://ab.bot/api/skills/{skill_id}
        """
        cipher = Fernet(safe_key)
        obj = cipher.decrypt(self._request_header)
        headers = json.loads(obj)

        url = self.base_url + path
        response = requests.get(url, headers=headers, verify=self.verify_ssl)
        if response.status_code == 200:
            output = response.json()
            return output
        elif response.status_code == 404:
            return None
        else:
            raise Exception("Failed with a status of {}".format(response.status_code))

    """
    Makes a POST request to the Abbot API.
    Arguments:
        path: The path to the resource to GET. This is the part after https://ab.bot/api/skills/{skill_id}
        data: The data to POST.
    """
    def post(self, path, data):
        url = self.base_url + path
        cipher = Fernet(safe_key)
        obj = cipher.decrypt(self._request_header)
        headers = json.loads(obj)

        try:
            result = requests.post(url, headers=headers, verify=self.verify_ssl, json=data)
            result.raise_for_status()
            return result.json()
        except Exception as e:
            logging.error("There was an error POSTing to {}".format(url))
            logging.error(e)

    """
    Makes a DELETE request to the Abbot API.
    Arguments:
        path: The path to the resource to GET. This is the part after https://ab.bot/api/skills/{skill_id}
    """
    def delete(self, path):
        url = self.base_url + path
        cipher = Fernet(safe_key)
        obj = cipher.decrypt(self._request_header)
        headers = json.loads(obj)
        return requests.delete(url, headers=headers, verify=self.verify_ssl)
