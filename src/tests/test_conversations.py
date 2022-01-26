import unittest

from datetime import datetime
from dateutil.tz import tzutc
from SkillRunner.bot.chat_address import ChatAddress, ChatAddressType

from SkillRunner.bot.conversations import Conversation
from SkillRunner.bot.platform_type import PlatformType
from SkillRunner.bot.rooms import Room
from SkillRunner.bot.mention import Mention, Location

class ConversationTest(unittest.TestCase):
    def test_parse_json(self):
        json = {
            "Id": "42",
            "FirstMessageId": "1111.2222",
            "Title": "Mako Reactor Job",
            "WebUrl": "https://ab.bot/conversations/42",
            "Room": {
                "Id": "C001",
                "Name": "avalanche-planning"
            },
            "StartedBy": {
                "Id": "U001",
                "UserName": "cloud",
                "Name": "Cloud Strife"
            },
            "Created": "2022-01-01T01:02:03.000000+00:00",
            "LastMessagePostedOn": "2022-01-02T01:02:03.000000+00:00",
            "Members": [
                {
                    "Id": "U001",
                    "UserName": "cloud",
                    "Name": "Cloud Strife",
                },
                {
                    "Id": "U002",
                    "UserName": "barret",
                    "Name": "Barret Wallace"
                },
                {
                    "Id": "U003",
                    "UserName": "tifa",
                    "Name": "Tifa Lockhart"
                },
            ]
        }
        convo = Conversation.from_json(json, PlatformType.SLACK)

        self.assertEqual("42", convo.id)
        self.assertEqual("Mako Reactor Job", convo.title)
        self.assertEqual("https://ab.bot/conversations/42", convo.web_url)
        self.assertEqual(Room("C001", "avalanche-planning", PlatformType.SLACK), convo.room)
        self.assertEqual(Mention("U001", "cloud", "Cloud Strife", None, Location(None, None, None), PlatformType.SLACK), convo.started_by)
        self.assertEqual(datetime(2022, 1, 1, 1, 2, 3, tzinfo=tzutc()), convo.created)
        self.assertEqual(datetime(2022, 1, 2, 1, 2, 3, tzinfo=tzutc()), convo.last_message_posted_on)
        self.assertEqual([
            Mention("U001", "cloud", "Cloud Strife", None, Location(None, None, None), PlatformType.SLACK),
            Mention("U002", "barret", "Barret Wallace", None, Location(None, None, None), PlatformType.SLACK),
            Mention("U003", "tifa", "Tifa Lockhart", None, Location(None, None, None), PlatformType.SLACK)
        ], convo.members)

        self.assertEqual(ChatAddress(ChatAddressType.ROOM, "C001", "1111.2222"), convo.get_chat_address())