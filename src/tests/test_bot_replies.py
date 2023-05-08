import json
from typing import Any, Optional
import unittest
import responses

from responses import matchers

from SkillRunner.bot.bot import Bot
from SkillRunner.bot.platform_type import PlatformType
from SkillRunner.bot.button import Button
from SkillRunner.bot.chat_address import ChatAddressType
from SkillRunner.bot.mention import Mention, TimeZone, Location, Coordinate
from SkillRunner.bot.room import Room

TEST_SKILL_ID = 42
TEST_FROM_USER = "U314"
TEST_MESSAGE_ID = "9999.1111"
TEST_ROOM = Room("C111", "#gaia")
SKILLS_API_BASE = f"https://localhost:4979/api/skills/{TEST_SKILL_ID}"
TEST_CONV_REFERENCE = {
    "Conversation": {
        "Id": "test_conversation_id"
    }
}
TEST_SEND_USER = Mention("U777", "cloud", "Cloud Strife", "cstrife@ava.lanche", Location(Coordinate(0, 0), "Midgar", TimeZone("America/Los_Angeles")))
TEST_SEND_ROOM = Room("C777", "#midgar")

class BotRepliesTest(unittest.TestCase):
    @responses.activate
    def test_reply(self):
        self.mockReply()

        bot = self.create_test_bot()
        bot.reply("Hello, World!")

        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], message="Hello, World!")

    @responses.activate
    def test_reply_with_dm_sets_to_field(self):
        self.mockReply()

        bot = self.create_test_bot()
        bot.reply("Hello, World!", direct_message=True)

        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], message="Hello, World!", options={
            "to": { "Type": ChatAddressType.USER.value, "Id": TEST_FROM_USER }
        })

    @responses.activate
    def test_reply_with_to_user(self):
        self.mockReply()

        bot = self.create_test_bot()
        bot.reply("Hello, World!", to=TEST_SEND_USER)
        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], message="Hello, World!", options={
            "to": { "Type": ChatAddressType.USER.value, "Id": TEST_SEND_USER.id }
        })

    @responses.activate
    def test_reply_with_to_user_thread(self):
        self.mockReply()

        bot = self.create_test_bot()
        bot.reply("Hello, World!", to=TEST_SEND_USER.get_thread("1234.5678"))
        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], message="Hello, World!", options={
            "to": { "Type": ChatAddressType.USER.value, "Id": TEST_SEND_USER.id, "ThreadId": "1234.5678" }
        })

    @responses.activate
    def test_reply_with_to_room(self):
        self.mockReply()

        bot = self.create_test_bot()
        bot.reply("Hello, World!", to=TEST_SEND_ROOM)

        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], message="Hello, World!", options={
            "to": { "Type": ChatAddressType.ROOM.value, "Id": TEST_SEND_ROOM.id }
        })

    @responses.activate
    def test_reply_with_to_thread(self):
        self.mockReply()

        bot = self.create_test_bot()
        bot.reply("Hello, World!", to=bot.thread)

        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], message="Hello, World!", options={
            "to": { "Type": ChatAddressType.ROOM.value, "Id": TEST_ROOM.id, "ThreadId": TEST_MESSAGE_ID }
        })

    @responses.activate
    def test_reply_with_to_room_thread(self):
        self.mockReply()

        bot = self.create_test_bot()
        bot.reply("Hello, World!", to=TEST_SEND_ROOM.get_thread("1234.5678"))

        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], message="Hello, World!", options={
            "to": { "Type": ChatAddressType.ROOM.value, "Id": TEST_SEND_ROOM.id, "ThreadId": "1234.5678" }
        })

    @responses.activate
    def test_reply_with_to_room_conversation(self):
        self.mockReply()

        bot = self.create_test_bot()
        room = bot.rooms.get_target("C1234")
        bot.reply("Hello, World!", to=room.get_thread("1234.5678"))

        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], message="Hello, World!", options={
            "to": { "Type": ChatAddressType.ROOM.value, "Id": "C1234", "ThreadId": "1234.5678" }
        })

    @responses.activate
    def test_reply_with_to_user_conversation(self):
        self.mockReply()

        bot = self.create_test_bot()
        user = bot.users.get_target("U1234")
        bot.reply("Hello, World!", to=user.get_thread("1234.5678"))

        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], message="Hello, World!", options={
            "to": { "Type": ChatAddressType.USER.value, "Id": "U1234", "ThreadId": "1234.5678" }
        })

    @responses.activate
    def test_reply_with_buttons(self):
        self.mockReply()

        bot = self.create_test_bot()
        bot.reply_with_buttons("Which is better?",
            buttons=[Button("Tabs"), Button("Spaces")],
            buttons_label="Label",
            image_url="ImageUrl",
            title="Title",
            color="#BEEFCAFE")

        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], message="Which is better?", attachments=[
            {
                "Buttons": [ Button("Tabs").toJSON(), Button("Spaces").toJSON() ],
                "ButtonsLabel": "Label",
                "ImageUrl": "ImageUrl",
                "Title": "Title",
                "Color": "#BEEFCAFE"
            }
        ])

    @responses.activate
    def test_reply_with_buttons_to(self):
        self.mockReply()

        bot = self.create_test_bot()
        bot.reply_with_buttons("Which is better?",
            buttons=[Button("Tabs"), Button("Spaces")],
            buttons_label="Label",
            image_url="ImageUrl",
            title="Title",
            color="#BEEFCAFE",
            to=TEST_SEND_USER)

        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], message="Which is better?", attachments=[
            {
                "Buttons": [ Button("Tabs").toJSON(), Button("Spaces").toJSON() ],
                "ButtonsLabel": "Label",
                "ImageUrl": "ImageUrl",
                "Title": "Title",
                "Color": "#BEEFCAFE"
            }
        ], options={
            "to": { "Type": ChatAddressType.USER.value, "Id": TEST_SEND_USER.id }
        })

    @responses.activate
    def test_reply_with_image(self):
        self.mockReply()

        bot = self.create_test_bot()
        bot.reply_with_image("ImageUrl",
            response="Here's a pretty picture",
            title="Title",
            title_url="TitleUrl",
            color="#BEEFCAFE")

        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], message="Here's a pretty picture", attachments=[
            {
                "Buttons": [],
                "ImageUrl": "ImageUrl",
                "Title": "Title",
                "TitleUrl": "TitleUrl",
                "Color": "#BEEFCAFE"
            }
        ])

    @responses.activate
    def test_reply_with_image_to(self):
        self.mockReply()

        bot = self.create_test_bot()
        bot.reply_with_image("ImageUrl",
            response="Here's a pretty picture",
            title="Title",
            title_url="TitleUrl",
            color="#BEEFCAFE",
            to=TEST_SEND_ROOM)

        self.assertEqual(1, len(responses.calls))
        self.assertReplyCall(responses.calls[0], "Here's a pretty picture", attachments=[
            {
                "Buttons": [],
                "ImageUrl": "ImageUrl",
                "Title": "Title",
                "TitleUrl": "TitleUrl",
                "Color": "#BEEFCAFE"
            }
        ], options={
            "to": { "Type": ChatAddressType.ROOM.value, "Id": TEST_SEND_ROOM.id }
        })

    
    def create_test_bot(self, **kwargs):
        req = {
            "SkillInfo": {
                "PlatformType": PlatformType.UNIT_TEST,
                "MessagePlatformType": PlatformType.UNIT_TEST,
                "Bot": {
                },
                "From": {
                    "Id": TEST_FROM_USER
                },
                "RoomId": TEST_ROOM.id,
                "Room": TEST_ROOM.name,
                "MessageId": TEST_MESSAGE_ID,
            },
            "RunnerInfo": {
                "SkillId": TEST_SKILL_ID,
                "ConversationReference": TEST_CONV_REFERENCE
            },
            "SignalInfo": {
            }
        }
        return Bot(req, "test_token", **kwargs)

    def mockReply(self, status=200):
        success = status >= 200 and status < 300
        responses.add(responses.POST, f"{SKILLS_API_BASE}/reply",
            json={
                "Success": success,
                "Message": "Message sent immediately" if success else "Error",
            },
            status=status)
    
    def assertReplyCall(self, response: responses.Call, message: Optional[str] = None, skillId: Optional[int]=None, conversationReference: Any=None, options={}, attachments=[], delayInSeconds=0):
        expected_json = {
            "SkillId": skillId or TEST_SKILL_ID,
            "Message": message,
            "ConversationReference": conversationReference or TEST_CONV_REFERENCE,
            "Options": options,
            "Attachments": attachments,
            "Schedule": delayInSeconds,
            "MessagePlatformType": "Slack",
        }

        self.assertEqual(responses.POST, response.request.method)
        self.assertEqual(f"{SKILLS_API_BASE}/reply", response.request.url)
        self.assertEqual("application/json", response.request.headers["Content-Type"])
        jbody = json.loads(responses.calls[0].request.body)
        self.assertEqual(expected_json, jbody)

if __name__ == '__main__':
    unittest.main()