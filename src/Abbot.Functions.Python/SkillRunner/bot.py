import os
import json
import sys
import requests
import logging
import traceback

# Imports solely for use in user skill
import pandas
import numpy
import bs4
import soupsieve
# End of user skill imports

from __app__.SkillRunner import storage 
from __app__.SkillRunner import secrets
from __app__.SkillRunner import exceptions
from __app__.SkillRunner.apiclient import ApiClient


class Mention(object):
    def __init__(self, Id, UserName, Name):
        self.id = Id
        self.user_name = UserName
        self.name = Name
    
    def toJSON(self):
            return json.dumps(self, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4)

    def __str__(self):
        return "<@{}>".format(self.user_name)


class Bot(object):
    def __init__(self, req, api_token):
        self.skill_id = req.get('SkillId')
        self.user_id = req.get('UserId')
        self.timestamp = req.get('Timestamp')

        bot_data = req.get('Bot')
        self.raw = req
        self.reply_api_uri = os.environ.get('AbbotReplyApiUrl', 'https://localhost:4979/api/reply')

        self.id = bot_data.get('Id')
        self.user_name = bot_data.get('UserName')
        self.args = req.get('Arguments')
        self.arguments = self.args
        self.code = req.get('Code')
        self.brain = storage.Brain(self.skill_id, self.user_id, api_token, self.timestamp)
        self.secrets = secrets.Secrets(self.skill_id, self.user_id, api_token, self.timestamp)
        
        self.from_user = req.get('From')
        self.mentions = self.load_mentions(req.get('Mentions'))

        if req.get('HttpTriggerEvent'):
            self.is_chat = True
        else:
            self.is_chat = False
        
        self.is_request = not self.is_chat

        self.request = bot_data.get('HttpTriggerEvent')
        self.conversation_reference = req.get('ConversationReference')

        self.api_client = ApiClient(self.reply_api_uri, self.user_id, api_token, self.timestamp)
        self.responses = []
    
    def run_user_script(self):
        """
        Run the code the user has submitted.
        """
        try:
            # Remove `os` from `sys` so users cannot use the module.
            os_copy = os
            sys.modules['os'] = None

            script_locals = { "bot": self, "args": self.args }
            out = None
            # Run the code
            exec(self.code, script_locals, script_locals)

            # Restore `os` so our code can use it if necessary.
            sys.modules['os'] = os_copy
            out = script_locals.get('bot')

            return out.responses
        except SyntaxError as e:
            description = "{}: {}".format(e.__class__.__name__, e.args[0])
            err = exceptions.InterpreterError("SyntaxError", description, e.lineno, 0)
            raise err
        except AttributeError as e:
            if not out:
                raise e
            if not out.__ScriptResponse__ or out.__ScriptResponse__ is None:
                err = exceptions.InterpreterError("NoResponseError", "You must call `bot.reply(<output>)` at least once with your output.", 0, 0)
                raise err
            else:
                pass
        except Exception as e:
            raise e

    
    def reply(self, response):        
        if self.conversation_reference:
            body = {"SkillId": self.skill_id, "Message": response, "ConversationReference": self.conversation_reference}
            self.api_client.post(self.reply_api_uri, body)
        else:
            self.responses.append(response)
    
    def reply_later(self, response, delay_in_seconds):
        if self.conversation_reference:
            body = {
                "SkillId": self.skill_id, 
                "Message": response, 
                "ConversationReference": self.conversation_reference, 
                "Schedule": delay_in_seconds
                }
            self.api_client.post(self.reply_api_uri, body)
        else:
            self.responses.append(response)


    def load_mentions(self, mentions):
        return [Mention(m.get('Id'), m.get('UserName'), m.get('Name')) for m in mentions]


    def __repr__(self):
        response = "A very nice bot with these features: \n"
        response += "       args: " + self.args + "\n "
        response += "  responses: " + '\n'.join(self.responses)

        return response