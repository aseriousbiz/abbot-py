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

from . import storage 
from . import secrets
from . import utils
from . import exceptions
from . import apiclient


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
    """
    Most interactions with the outside world occur from the Bot object.
    Abbot injects this object into your script as ``bot``.
    """
    def __init__(self, req, api_token):
        self.skill_id = req.get('SkillId')
        self.user_id = req.get('UserId')
        self.timestamp = req.get('Timestamp')

        bot_data = req.get('Bot')
        self.raw = req
        self.reply_api_uri = os.environ.get('AbbotReplyApiUrl', 'https://localhost:4979/api/reply')

        self.id = bot_data.get('Id') #: The Bot's Id
        self.user_name = bot_data.get('UserName') #: The Bot's Username
        self.args = req.get('Arguments') #: Arguments from the user
        self.arguments = self.args #: Arguments from the user
        self.code = req.get('Code')
        self.brain = storage.Brain(self.skill_id, self.user_id, api_token, self.timestamp) #: Instantation of Brain as bot.brain
        self.secrets = secrets.Secrets(self.skill_id, self.user_id, api_token, self.timestamp) #: Instantiation of Secrets as bot.secrets
        self.utils = utils.Utilities(self.skill_id, self.user_id, api_token, self.timestamp) #: Instantiation of Utilities at bot.utils
        
        self.from_user = req.get('From') #: The user who sent the message
        self.mentions = self.load_mentions(req.get('Mentions')) #: A collection of user mentions

        if req.get('HttpTriggerEvent'):
            self.is_chat = False  #: is_chat is set to False if the request is the result of a trigger. True otherwise.
            self.is_request = True #: is_request is set to True if the request is the result of a trigger. False otherwise.
        else:
            self.is_chat = True
            self.is_request = False

        self.request = bot_data.get('HttpTriggerEvent') #: The http request that triggered this message
        self.conversation_reference = req.get('ConversationReference')

        self.api_client = apiclient.ApiClient(self.reply_api_uri, self.user_id, api_token, self.timestamp)
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
            raise e
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
        """
        Send a reply. 
        
        Args:
            response (str): The response to send back to chat.
        """   
        if self.conversation_reference:
            body = {"SkillId": self.skill_id, "Message": str(response), "ConversationReference": self.conversation_reference}
            self.api_client.post(self.reply_api_uri, body)
        else:
            self.responses.append(str(response))
    
    def reply_later(self, response, delay_in_seconds):
        """
        Reply after a delay.

        Args:
            response (str): The response to send back to chat.
            delay_in_seconds (int): The number of seconds to delay before sending the response.
        """
        if self.conversation_reference:
            body = {
                "SkillId": self.skill_id, 
                "Message": str(response), 
                "ConversationReference": self.conversation_reference, 
                "Schedule": delay_in_seconds
                }
            self.api_client.post(self.reply_api_uri, body)
        else:
            self.responses.append(str(response))


    def load_mentions(self, mentions):
        return [Mention(m.get('Id'), m.get('UserName'), m.get('Name')) for m in mentions]


    def __repr__(self):
        response = "Abbot: "
        response += "   args: " + self.args + "\n "
        response += "    raw: " + self.raw

        return response