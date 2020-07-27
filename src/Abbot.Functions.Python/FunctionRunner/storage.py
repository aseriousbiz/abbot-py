import os
import requests

class Brain(object):
    def __init__(self, skill, userid, requestToken):
        self.skill = skill
        self.userid = userid
        self.requestUri = os.environ.get('UserSkillApiUriFormatString', 'https://localhost:4979/api/skill/{0}/data/{1}')
        self.requestHeader = {'X-Abbot-SkillApiToken': requestToken}

    def makeUri(self, key, id):
        return self.requestUri.format(key, id)

    def write(self, key, value):
        uri = self.makeUri(key, self.userid)
        return requests.post(uri, header=self.requestHeader, body={"Value": value})

    def update(self, key, value):
        # Is this needed? 
        self.write(key, value)

    def search(self, term):
        raise NotImplementedError
    
    def list(self):
        raise NotImplementedError
    
    def delete(self, key):
        uri = self.makeUri(key, self.userid)
        return requests.delete(uri, header=self.requestHeader)
    
    def __str__(self):
        return "Brain for {} skill.".format(self.skill)

    def __repr__(self):
        return "Brain for {} skill.".format(self.skill)