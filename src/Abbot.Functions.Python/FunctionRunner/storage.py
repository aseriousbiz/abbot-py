import os
import requests

class Brain(object):
    def __init__(self, skill_id, user_id, request_token):
        self.skill_id = skill_id
        self.user_id = user_id
        self.request_uri = os.environ.get('UserSkillApiUriFormatString', 'https://localhost:4979/api/skill/{0}/data/{1}')
        self.request_header = {'X-Abbot-SkillApiToken': request_token}

    def make_uri(self, key, id):
        return self.request_uri.format(key, id)

    def read(self, key):
        uri = self.make_uri(key, self.user_id)
        return requests.get(uri, headers=self.request_header)

    def write(self, key, value):
        uri = self.make_uri(key, self.user_id)
        return requests.post(uri, headers=self.request_header, params={"Value": value})

    def update(self, key, value):
        # Is this needed? 
        self.write(key, value)

    def search(self, term):
        raise NotImplementedError
    
    def list(self):
        raise NotImplementedError
    
    def delete(self, key):
        uri = self.make_uri(key, self.user_id)
        return requests.delete(uri, headers=self.request_header)

    def test(self, key):
        return "You sent '{}' to the brain.".format(key)
    
    def __str__(self):
        return "Brain for {} skill.".format(self.skill)

    def __repr__(self):
        return "Brain for {} skill.".format(self.skill)