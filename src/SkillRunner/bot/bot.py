# pylint: disable=unused-import
import os
import json
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
from .users import Users
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
from .customers_client import CustomerRequest, CustomersClient
from .tickets_client import TicketsClient
from . import exceptions
from .apiclient import ApiClient
from .trigger_response import TriggerResponse
from .button import Button
from .arguments import Argument, MentionArgument, Arguments, RoomArgument
from .message_options import MessageOptions
from .conversations import Conversation
from .policy import get_policy
from .source_message import SourceMessage

class Bot(object):
    """
    Most interactions with the outside world occur from the Bot object.
    Abbot injects this object into your script as ``bot``.

    :var id: The Bot's Id.
    :var name: The Bot's user name.
    :var skill_id: The ID of the skill being invoked.
    :var user_id: The ID of the user invoking the skill.
    :var timestamp: The timestamp of the invocation.
    :var code: The code submitted by the user.
    :var room: The room the user invoked the skill in.
    :var message_id: The platform-specific ID of the message that triggered the invocation, if any
    :var thread: The thread the user invoked the skill in.
    :var brain: A client to access skill data in Abbot's Brain.
    :var secrets: A client to access skill secrets.
    :var rooms: A client to manage Rooms.
    :var users: A client to manage Users.
    :var utils: Some utilities for skill authors.
    :var raw: The raw skillInfo object.
    :var user_name: The user name of the user invoking the skill.
    :var args: The arguments passed to the skill (alias for arguments).
    :var arguments: The arguments passed to the skill.
    :var pattern: The pattern that was matched, if any.
    :var is_pattern_match: Whether or not the skill was invoked by a pattern.
    :var platform_id: The ID of the team the skill was invoked by.
    :var skill_name: The name of the skill being invoked.
    :var skill_url: The URL of the skill being invoked.
    :var from_user: The user invoking the skill.
    :var mentions: The users mentioned in the message that triggered the skill.
    :var tokenized_arguments: The arguments passed to the skill, tokenized.
    :var is_interaction: Whether or not the skill was invoked as an interaction.
    :var is_request: Whether or not the skill was invoked from an HTTP request.
    :var is_chat: Whether or not the skill was invoked as a chat message.
    :var request: The request that triggered the skill, if any.
    :var response: The response that will be sent to the sender of the HTTP request, if any.
    :var conversation: The conversation this skill was invoked within, if any.
    """
    def __init__(self, req, api_token, trace_parent=None, logger=None):
        self.responses = []
        self.logger = logger or logging.getLogger("Bot")

        skillInfo = req.get('SkillInfo')
        runnerInfo = req.get('RunnerInfo')
        self.platform_type = PlatformType.parse(skillInfo.get('PlatformType'))
        self.conversation = Conversation.from_json(req.get('ConversationInfo'), self.platform_type)
        
        self._signal_info = req.get('SignalInfo')
        self._signal_event = None

        self.id = skillInfo.get('Bot').get('Id')
        self.name = skillInfo.get('Bot').get('Name')
        self.skill_id = runnerInfo.get('SkillId')
        self.user_id = runnerInfo.get('UserId')
        self.timestamp = runnerInfo.get('Timestamp')
        self.code = runnerInfo.get('Code')
        self.room = Room.from_json(skillInfo)
        self.message_id = skillInfo.get('MessageId')
        thread_id = skillInfo.get('ThreadId') or self.message_id
        self.thread = self.room.get_thread(thread_id)
        self.message = SourceMessage.from_json(skillInfo.get('Message'))

        # Clients
        api_client = ApiClient(self.skill_id, self.user_id, api_token, self.timestamp, trace_parent, self.logger.getChild("ApiClient"))
        self.brain = Brain(api_client) 
        self.secrets = Secrets(api_client)
        self.rooms = Rooms(api_client, self.platform_type)
        self.users = Users(api_client)
        self.utils = Utilities(api_client)
        self._signaler = Signaler(api_client, req)
        self._reply_client = ReplyClient(api_client, self.room, thread_id, req.get('PassiveReplies'), runnerInfo.get('ConversationReference'), self.skill_id, self.responses)
        self._tickets_client = TicketsClient(api_client, self)
        self.customers = CustomersClient(api_client)

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
                "CustomerRequest": CustomerRequest,
                "PatternType": pattern.PatternType,
                "Argument": Argument,
                "MentionArgument": MentionArgument,
                "RoomArgument": RoomArgument,
            }

            out = None

            policy_name = os.environ.get("ABBOT_SANDBOX_POLICY")
            if policy_name is None:
                if os.environ.get("ABBOT_SANDBOXED") == "false":
                    policy_name = "permissive"
                else:
                    policy_name = "restrictive"

            policy = get_policy(policy_name, self.logger.getChild("Policy"))
            self.logger.info("Running user script under %s policy.", policy.name())
            policy.exec(self.code, script_locals)

            return self.responses
        except SyntaxError as e:
            self.logger.exception("Compilation Error", exc_info=True)
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
            self.logger.exception("Runtime Error", exc_info=True)
            raise e

    def reply(self, response, direct_message=False, **kwargs):
        """
        Send a reply. If direct_message is True, then the reply is sent as a direct message to the caller.
        
        Args:
            response (str): The response to send back to chat.
        
        Keyword Args:
            to (Union[RoomMessageTarget,UserMessageTarget,ChatAddress]): The recipient of the reply.
        """
        if direct_message:
            kwargs['to'] = self.from_user
        options = MessageOptions(self, **kwargs)

        self._reply_client.reply(response, options)

    def reply_with_buttons(self, response, buttons, buttons_label=None, image_url=None, title=None, color=None, **kwargs):
        """
        Sends a reply with a set of buttons. Clicking a button will call back into this skill.

        Args:
            response (str): The message to send as a response.
            buttons (list[Button]): The set of buttons to display (Maximum 6).
            buttons_label (str): The text that serves as a label for the set of buttons (optional).
            image_url (str): An image to render before the set of buttons (optional).
            title (str): A title to render (optional).
            color (str): The color to use for the sidebar (Slack Only) in hex (ex. #3AA3E3) (optional).
        
        Keyword Args:
            to (Union[RoomMessageTarget,UserMessageTarget,ChatAddress]): The recipient of the reply.
        """
        options = MessageOptions(self, **kwargs)
        self._reply_client.reply_with_buttons(response, buttons, buttons_label, image_url, title, color, options)

    def reply_with_image(self, image, response=None, title=None, title_url=None, color=None, **kwargs):
        """
        Sends a reply along with an image attachment. The image can be a URL to an image or a base64 encoded image.

        Args:
            image (str): Either the URL to an image or the base64 encoded image.
            response (str): The message to send as a response (optional).
            title (str): An image title to render (optional).
            title_url (str): If specified, makes the title a link to this URL. Ignored if title is not set. (optional).
            color (str): The color to use for the sidebar (Slack Only) in hex (ex. #3AA3E3) (optional).
        
        Keyword Args:
            to (Union[RoomMessageTarget,UserMessageTarget,ChatAddress]): The recipient of the reply.
        """
        options = MessageOptions(self, **kwargs)
        self._reply_client.reply_with_image(image, response, title, title_url, color, options)

    def reply_later(self, response, delay_in_seconds, **kwargs):
        """
        Reply after a delay.

        Args:
            response (str): The response to send back to chat.
            delay_in_seconds (int): The number of seconds to delay before sending the response.
        
        Keyword Args:
            to (Union[RoomMessageTarget,UserMessageTarget,ChatAddress]): The recipient of the reply.
        """
        options = MessageOptions(self, **kwargs)
        self._reply_client.reply_later(response, delay_in_seconds, options)

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
