import json
import requests
import logging
import os

from cryptography.fernet import Fernet
from urllib.error import HTTPError

from .utils import Environment

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
    def __init__(self, skill_id, user_id, api_token, timestamp, trace_parent, logger=None):
        self.user_id = user_id
        self.logger = logger or logging.getLogger("ApiClient")

        base_url = os.environ.get('AbbotApiBaseUrl', 'https://localhost:4979/api')
        self.base_url = f'{base_url}/skills/{skill_id}'

        if self.base_url.startswith("https://localhost") or self.base_url.startswith("https://host.docker.internal"):
            self.verify_ssl = False
        else:
            self.verify_ssl = True

        header_obj = {
                'Content-Type': 'application/json',
                'X-Abbot-SkillApiToken': api_token, 
                'X-Abbot-PlatformUserId': str(user_id),
                'X-Abbot-Timestamp': str(timestamp),
                'Authorization': f'Bearer {api_token}',
                'traceparent': trace_parent
            }
        self.logger.info('ApiClient created with traceparent: %s', trace_parent)
        
        # In order to prevent users from accessing sensitive data, we encrypt it using Fernet, 
        # then decrypt in the accessors. 
        obj = json.dumps(header_obj).encode('utf-8')
        cipher = Fernet(safe_key)
        self._request_header = cipher.encrypt(obj)

    def get(self, path):
        """
        Makes a GET request to the Abbot API.
        Arguments:
            path: The path to the resource to GET. This is the part after https://ab.bot/api/skills/{skill_id}
        """
        return self.send(path, 'GET')

    def post(self, path, data=None):
        """
        Makes a POST request to the Abbot API.
        Arguments:
            path: The path to the resource to POST. This is the part after https://ab.bot/api/skills/{skill_id}
            data: The data to POST.
        """
        return self.send(path, 'POST', data)

    def put(self, path, data=None):
        """
        Makes a PUT request to the Abbot API.
        Arguments:
            path: The path to the resource to PUT. This is the part after https://ab.bot/api/skills/{skill_id}
            data: The data to PUT.
        """
        return self.send(path, 'PUT', data)

    def send(self, path, method, data=None):
        """
        Sends a request to the Abbot API.
        Arguments:
            path: The path to the resource to POST. This is the part after https://ab.bot/api/skills/{skill_id}
            method: The HTTP method to use.
            data: The data to POST.
        """
        url = self.base_url + path
        cipher = Fernet(safe_key)
        obj = cipher.decrypt(self._request_header)
        headers = json.loads(obj)

        try:
            result = requests.request(method, url, headers=headers, verify=self.verify_ssl, json=data)
            result.raise_for_status()
            if len(result.text) > 0:
                return result.json()
            else:
                return None
        except Exception as e:
            if Environment.is_test():
                raise e
            self.logger.exception("There was an error %s ing to %s", method, path)
            raise Exception("Failed to communicate with Abbot.")

    def delete(self, path):
        """
        Makes a DELETE request to the Abbot API.
        Arguments:
            path: The path to the resource to DELETE. This is the part after https://ab.bot/api/skills/{skill_id}
        """
        return self.send(path, 'DELETE')

