import os
import json
import sys
import jsonpickle
import requests
import logging
import traceback

# Imports solely for use in user skill
import pandas
import numpy
import bs4
import soupsieve
import boto3
import octokit
# End of user skill imports

from . import storage 
from . import secrets
from . import utils
from . import exceptions
from . import apiclient


class TriggerEvent(object):
    """
    A request triggered by an external event.

    :var content_type: The Content Type of the request.
    :var http_method: The Http Method of the request.
    :var is_form: True if the request is a form. Otherwise False.
    :var is_json: True if the request contains json data. Otherwise False.
    :var headers: The request headers.
    :var form: Form data, if it exists.
    :var query: QueryString data, if it exists.
    :var url: The request url.
    :var raw_body: The raw body of the request.
    """
    def __init__(self, request):
        self.content_type = request.get('ContentType')
        self.http_method = request.get('HttpMethod')
        self.is_form = request.get('IsForm')
        self.is_json = request.get('IsJson')
        self.headers = request.get('Headers')
        self.form = request.get('Form')
        self.query = request.get('Query')
        self.url = request.get('Url')
        self.raw_body = request.get('RawBody')
    
    def toJSON(self):
        return jsonpickle.encode(self)


class Mention(object):
    """
    A User mention.

    :var id: The User's Id.
    :var user_name: The User's user name.
    :var name: The User's name.
    """
    def __init__(self, Id, UserName, Name):
        self.id = Id
        self.user_name = UserName
        self.name = Name
    
    def toJSON(self):
            return json.dumps(self, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4)

    def __str__(self):
        return "<@{}>".format(self.user_name)

class FakeOS(object):
    """
    Used to pass into the skill runner. 
    Every method call returns None, but lets libraries that
    rely on the existence of the `os` module continue running.
    """
    def __getattr__(self, name):
        def method(*args):
            return None


class Bot(object):
    """
    Most interactions with the outside world occur from the Bot object.
    Abbot injects this object into your script as ``bot``.

    :var id: The Bot's Id.
    :var user_name: The Bot's user name.
    :var from_user: The name of the user who called the skill.
    :var args: Arguments from the user.
    :var arguments: Arguments from the user.
    :var mentions: A collection of user mentions.
    :var is_chat: True if the message came from chat. False if not. 
    :var is_request: True if the message came from a trigger. False if not.
    :var platform_id: The id of the team this skill is being run in. This would be your Team Id in Slack, for example.
    :var platform_type: The type of platform, such as Slack, Teams, or Discord.
    :var room: The room the skill is being run in.
    :var skill_name: The name of the skill being run.
    :var skill_url: The URL to the edit screen of the skill being run.
    """
    def __init__(self, req, api_token):
        self.reply_api_uri = os.environ.get('AbbotReplyApiUrl', 'https://ab.bot/api/reply')
        skillInfo = req.get('SkillInfo')
        runnerInfo = req.get('RunnerInfo')

        self.skill_id = runnerInfo.get('SkillId')
        self.user_id = runnerInfo.get('UserId')
        self.timestamp = runnerInfo.get('Timestamp')
        

        bot_data = runnerInfo.get('Bot')
        self.raw = skillInfo
        

        self.id = runnerInfo.get('Id') 
        self.user_name = skillInfo.get('UserName') 
        self.args = skillInfo.get('Arguments') 
        self.arguments = self.args 
        self.code = runnerInfo.get('Code')
        self.brain = storage.Brain(self.skill_id, self.user_id, api_token, self.timestamp) 
        self.secrets = secrets.Secrets(self.skill_id, self.user_id, api_token, self.timestamp)
        self.utils = utils.Utilities(self.skill_id, self.user_id, api_token, self.timestamp)
        self.platform_id = skillInfo.get('PlatformId')
        self.platform_type = skillInfo.get('PlatformType')
        self.room = skillInfo.get('Room')
        self.skill_name = skillInfo.get('SkillName')
        
        self.from_user = skillInfo.get('From')
        self.mentions = self.load_mentions(skillInfo.get('Mentions'))

        self.is_request = skillInfo.get("IsRequest")
        self.is_chat = not self.is_request

        if self.is_request:
            self.request = TriggerEvent(skillInfo.get('Request'))
        else:
            self.request = None

        self.conversation_reference = runnerInfo.get('ConversationReference')

        self.api_client = apiclient.ApiClient(self.reply_api_uri, self.user_id, api_token, self.timestamp)
        self.responses = []
    
    def run_user_script(self):
        """
        Run the code the user has submitted.
        """
        try:
            # Many libraries rely on a real environ object, can't set this to None
            old_environ = dict(os.environ)
            os.environ.clear()

            deny = [
                '_execvpe', 'chmod', 'chown', 'chroot', 'execl', 'execle', 'execlp', 'execlpe', 'execv', 'execve', 'execvp', 
                'execvpe', 'kill', 'killpg', 'lchmod', 'lchown', 'link', 'posix_spawn', 'posix_spawnp','spawnl', 'spawnle', 
                'spawnlp', 'spawnlpe', 'spawnv', 'spawnve', 'spawnvp', 'spawnvpe', 'symlink']
            
            # Remove any object from os that hasn't been explicity whitelisted.
            for attr, value in os.__dict__.items():
                if attr in deny:
                    setattr(os, attr, lambda self: PermissionError("Access to this module (os.{}) is denied".format(attr)))

            script_locals = { "bot": self, "args": self.args }
            out = None
            # Run the code

            exec(self.code, script_locals, script_locals)

            # Restore the environment so the rest of the runner can use it.
            os.environ.update(old_environ) 

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
            logging.error(e)
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