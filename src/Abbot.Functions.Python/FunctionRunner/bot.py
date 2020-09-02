from __app__.FunctionRunner import storage 
from __app__.FunctionRunner import secrets

class Bot(object):
    def __init__(self, req, api_token):
        code = req.get('Code')
        skill_id = req.get('SkillId')
        user_id = req.get('UserId')
        timestamp = req.get('Timestamp')

        self.args = req.get('Arguments')
        self.brain = storage.Brain(skill_id, user_id, api_token, timestamp)
        self.secrets = secrets.Secrets(skill_id, user_id, api_token, timestamp)
    
    def reply(self, response):
        global __ScriptResponse__
        __ScriptResponse__ = response
