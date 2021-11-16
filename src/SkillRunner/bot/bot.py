import os
import json
from typing import Pattern
import jsonpickle
import requests
import logging
from unittest.mock import patch

# Imports solely for use in user skill
import pandas
import numpy
import bs4
import soupsieve
import boto3
import octokit
# End of user skill imports

from .storage import Brain
from .secrets import Secrets
from .rooms import Rooms
from .utils import Utilities
from .mention import Mention
from .room import Room
from .platform_type import PlatformType
from .trigger_event import TriggerEvent
from . import pattern
from . import signal_event
from .signaler import Signaler
from .utils import obj
from .reply_client import ReplyClient
from . import exceptions
from .apiclient import ApiClient
from .trigger_response import TriggerResponse
from .button import Button
from .arguments import Argument, MentionArgument, Arguments, RoomArgument
from types import SimpleNamespace


class Bot(object):
    """
    Most interactions with the outside world occur from the Bot object.
    Abbot injects this object into your script as ``bot``.

    :var id: The Bot's Id.
    :var user_name: The Bot's user name.
    :var from_user: A User object that represents the person who called the skill.
    :var args: Arguments from the user.
    :var arguments: Arguments from the user.
    :var mentions: A collection of user mentions.
    :var is_interaction: True if the message came from a user interacting with a UI element in chat such as clicking on a button. False if not.
    :var is_chat: True if the message came from chat. False if not. 
    :var is_request: True if the message came from a trigger. False if not.
    :var platform_id: The id of the team this skill is being run in. This would be your Team Id in Slack, for example.
    :var platform_type: The type of platform, such as Slack, Teams, or Discord.
    :var room: The room the skill is being run in.
    :var skill_name: The name of the skill being run.
    :var skill_url: The URL to the edit screen of the skill being run.
    """
    def __init__(self, req, api_token, trace_parent):
        self.responses = []

        skillInfo = req.get('SkillInfo')
        runnerInfo = req.get('RunnerInfo')
        self.platform_type = PlatformType(skillInfo.get('PlatformType'))
        
        self._signal_info = req.get('SignalInfo')
        self._signal_event = None

        self.id = skillInfo.get('Bot').get('Id')
        self.name = skillInfo.get('Bot').get('Name')
        self.skill_id = runnerInfo.get('SkillId')
        self.user_id = runnerInfo.get('UserId')
        self.timestamp = runnerInfo.get('Timestamp')
        self.code = runnerInfo.get('Code')
        self.room = Room.from_json(skillInfo)

        # Clients
        api_client = ApiClient(self.skill_id, self.user_id, api_token, self.timestamp, trace_parent)
        self.brain = Brain(api_client) 
        self.secrets = Secrets(api_client)
        self.rooms = Rooms(api_client, self.platform_type)
        self.utils = Utilities(api_client)
        self._reply_client = ReplyClient(api_client, runnerInfo.get('ConversationReference'), self.skill_id, self.responses)
        self._signaler = Signaler(api_client, req)

        self.raw = skillInfo

        # Properties for skill authors to consume
        self.user_name = skillInfo.get('UserName')
        self.args = skillInfo.get('Arguments')
        self.arguments = self.args
        patternRequest = skillInfo.get('Pattern')
        self.pattern = None if patternRequest is None else pattern.Pattern(patternRequest)
        self.is_pattern_match = self.pattern is not None
        self.platform_id = skillInfo.get('PlatformId')
        self.skill_name = skillInfo.get('SkillName')
        self.skill_url = skillInfo.get('SkillUrl')
        self.from_user = Mention.from_json(skillInfo.get('From'))
        self.mentions = Mention.load_mentions(skillInfo.get('Mentions'))
        args_json = skillInfo.get('TokenizedArguments', [])
        self.tokenized_arguments = Arguments.from_json(args_json, self.arguments, self.platform_type)

        self.is_interaction = skillInfo.get('IsInteraction')
        self.is_request = skillInfo.get('IsRequest')
        self.is_chat = not self.is_request
        
        if self.is_request:
            self.request = TriggerEvent(skillInfo.get('Request'))
            self.response = TriggerResponse()
        else:
            self.request = None

        # Load the full skillInfo object for debugging purposes. Don't document it for users.
        skillInfo['from_name'] = skillInfo['From']
        del skillInfo['From'] # `from` is a protected Python keyword, and can't be converted to an object
        self.skill_data = obj(skillInfo)


    def run_user_script(self):
        """
        Run the code the user has submitted.
        """
        try:
            script_locals = {
                "bot": self,
                "args": self.args,
                "Button": Button,
                "PatternType": pattern.PatternType,
                "Argument": Argument,
                "MentionArgument": MentionArgument,
                "RoomArgument": RoomArgument
            }
            out = None
            
            with patch.dict("os.environ", {}):
                # Clear os.environ, then run the code
                os.environ.clear()
                exec(self.code, script_locals, script_locals)

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


    def reply(self, response, direct_message=False):
        """
        Send a reply. If direct_message is True, then the reply is sent as a direct message to the caller.
        
        Args:
            response (str): The response to send back to chat.
        """
        self._reply_client.reply(response, direct_message)


    def reply_with_buttons(self, response, buttons, buttons_label=None, image_url=None, title=None, color=None):
        """
        Sends a reply with a set of buttons. Clicking a button will call back into this skill.

        Args:
            response (str): The message to send as a response.
            buttons (list[Button]): The set of buttons to display (Maximum 6).
            buttons_label (str): The text that serves as a label for the set of buttons (optional).
            image_url (str): An image to render before the set of buttons (optional).
            title (str): A title to render (optional).
            color (str): The color to use for the sidebar (Slack Only) in hex (ex. #3AA3E3) (optional).
        """
        self._reply_client.reply_with_buttons(response, buttons, buttons_label, image_url, title, color)


    def reply_with_image(self, image, response=None, title=None, title_url=None, color=None):
        """
        Sends a reply along with an image attachment. The image can be a URL to an image or a base64 encoded image.

        Args:
            image (str): Either the URL to an image or the base64 encoded image.
            response (str): The message to send as a response (optional).
            title (str): An image title to render (optional).
            title_url (str): If specified, makes the title a link to this URL. Ignored if title is not set. (optional).
            color (str): The color to use for the sidebar (Slack Only) in hex (ex. #3AA3E3) (optional).
        """
        self._reply_client.reply_with_image(image, response, title, title_url, color)


    def reply_later(self, response, delay_in_seconds):
        """
        Reply after a delay.

        Args:
            response (str): The response to send back to chat.
            delay_in_seconds (int): The number of seconds to delay before sending the response.
        """
        self._reply_client.reply_later(response, delay_in_seconds)


    def __str__(self):
        return f"<@{self.id}>" if self.platform_type == PlatformType.SLACK else f"@{self.name}"


    def __repr__(self):
        response = "Abbot: "
        response += "   args: " + self.args + "\n "
        response += "    raw: " + self.raw

        return response


    @property
    def signal_event(self):
        """
        The SignalEvent that this source skill is responding to, if any.
        """
        if (self._signal_event is None):
            self._signal_event = signal_event.SignalEvent(self._signal_info) if self._signal_info is not None else None
        return self._signal_event


    def signal(self, name, args):
        """
        Raises a signal from the skill with the specified name and arguments.
        Args:
            name (str): The name of the signal to raise.
            args (str): The arguments to pass to the skills that are subscribed to this signal.
        """
        return self._signaler.signal(name, args)