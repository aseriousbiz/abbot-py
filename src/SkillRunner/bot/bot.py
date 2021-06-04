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
    A user mention.

    :var id: The user's Id.
    :var user_name: The user's user name.
    :var name: The user's name.
    :var location: The user's location if known.
    :var timezone: The user's timezone if known
    """
    def __init__(self, id, user_name, name, location, timezone):
        self.id = id
        self.user_name = user_name
        self.name = name
        self.location = location
        self.timezone = timezone


    def toJSON(self):
            return json.dumps(self, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4)


    def __str__(self):
        return "<@{}>".format(self.user_name)


class Coordinate(object):
    """
    Represents a geographic coordinate.

    :var latitude: The latitude. Those are the lines that are the belts of the earth.
    :var longitude: The longitude. Those are the pin stripes of the earth.
    """
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return "lat: {}, lon: {}".format(self.latitude, self.longitude)


class Location(object):
    """
    A geo-coded location

    :var coordinate: The coordinates of the location.
    :var formatted_address: The formatted address of the location.
    """
    def __init__(self, coordinate, formatted_address):
        self.coordinate = coordinate
        self.formatted_address = formatted_address

    def __str__(self):
        return "coordinate: {}, address: {}".format(self.coordinate, self.formatted_address)


class TimeZone(object):
    """
    Information about a user's timezone

    :var id: The provider's ID for the timezone. Could be IANA or BCL.
    :var min_offset: Gets the least (most negative) offset within this time zone, over all time.
    :var max_offset: Gets the greatest (most positive) offset within this time zone, over all time.
    """
    def __init__(self, id, min_offset=None, max_offset=None):
        self.id = id
        self.min_offset = min_offset
        self.max_offset = max_offset

    def __str__(self):
        return "id: {}, min_offset: {}, max_offset: {}".format(self.id, self.min_offset, self.max_offset)


class Argument(object):
    """
    An argument parsed from the bot.arguments property. Arguments may be delimited by a space or 
    by a matching pair of quotes.

    :var value: The normalized argument value
    :var original_text: The original argument value. For quoted values this would include the surrounding quotes.
    """
    def __init__(self, value, original_text):
        self.value = value
        self.original_text = original_text


    def __str__(self):
        return self.value


class MentionArgument(Argument):
    """
    An argument that represents a mentioned user.
    """
    def __init__(self, value, original_text, mentioned):
        super().__init__(value, original_text)
        self.mentioned = mentioned

    def __str__(self):
        return "mentioned: {}".format(self.mentioned)


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
        self.reply_api_uri = os.environ.get('AbbotReplyApiUrl', 'https://ab.bot/api/reply') #TODO: change failure mode back to localhost.
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
        self.tokenized_arguments = self.load_arguments(skillInfo.get('TokenizedArguments', []))

        self.is_request = skillInfo.get('IsRequest')
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
            script_locals = { "bot": self, "args": self.args }
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


    def load_coordinate(self, coordinate_arg):
        return None if coordinate_arg is None else Coordinate(coordinate_arg.get('Latitude'), coordinate_arg.get('Longitude'))


    def load_location(self, location_arg):
        coordinate_arg = location_arg.get('Coordinate')
        coordinate = self.load_coordinate(coordinate_arg)
        return Location(coordinate, location_arg.get('FormattedAddress'))


    def load_timezone(self, tz_arg):
        return TimeZone(tz_arg.get('Id'), tz_arg.get('MinOffset'), tz_arg.get('MaxOffset'))


    def load_mention(self, mention):
        location_arg = mention.get('Location')
        timezone_arg = mention.Get('TimeZone')
        location = self.load_location(location_arg) if location_arg is not None else None
        timezone = self.load_timezone(timezone_arg) if timezone_arg is not None else None
        # Special case for PlatformUser mentions
        if (location_arg is not None and timezone is None):
            tz_id = location_arg.get('TimeZoneId')
            if tz_id is not None:
                timezone = TimeZone(tz_id)
        return Mention(mention.get('Id'), mention.get('UserName'), mention.get('Name'), location, timezone)


    def load_mentions(self, mentions):
        return [self.load_mention(m) for m in mentions]


    def load_argument(self, argument):
        value = argument.get('Value')
        original_text = argument.get('OriginalText')
        mentioned_arg = argument.get('Mentioned')
        mentioned = self.load_mention(mentioned_arg) if mentioned_arg is not None else None
        return Argument(value, original_text) if mentioned is None else MentionArgument(value, original_text, mentioned)


    def load_arguments(self, tokenized_arguments):
        return [self.load_argument(arg) for arg in tokenized_arguments]


    def __repr__(self):
        response = "Abbot: "
        response += "   args: " + self.args + "\n "
        response += "    raw: " + self.raw

        return response