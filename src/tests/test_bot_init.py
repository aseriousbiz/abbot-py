import unittest

from SkillRunner.bot.platform_type import PlatformType
from SkillRunner.bot.bot import Bot
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

class BotInitTest(unittest.TestCase):
    def test_read_conversation_from_SkillInfo(self):
        bot = self.create_test_bot({
            "ConversationInfo": {
                "Id": "42"
            }
        })
        self.assertEqual("42", bot.conversation.id)

    def test_init_with_room_id_and_name(self):
        req = {
            "SkillInfo": {
                "RoomId": "C999",
                "Room": "midgar",
            },
        }
        b = self.create_test_bot(req)
        self.assertEqual("C999", b.room.id)
        self.assertEqual("midgar", b.room.name)

    def test_init_with_room_object(self):
        req = {
            "SkillInfo": {
                "Room": { "Id": "C999", "Name": "midgar" },
            },
        }
        b = self.create_test_bot(req)
        self.assertEqual("C999", b.room.id)
        self.assertEqual("midgar", b.room.name)

    def create_test_bot(self, additional_request_body = {}):
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
                "RoomName": TEST_ROOM.name,
                "MessageId": TEST_MESSAGE_ID,
            },
            "RunnerInfo": {
                "SkillId": TEST_SKILL_ID,
                "ConversationReference": TEST_CONV_REFERENCE
            },
            "SignalInfo": {
            }
        }

        dict_merge(req, additional_request_body)
        return Bot(req, "test_token")

def dict_merge(a, b, path=None):
    # Good ol' Stack Overflow: https://stackoverflow.com/a/7205107
    if path is None: path = []
    for key in b:
        if key in a and isinstance(b[key], dict):
            if not isinstance(a[key], dict):
                a[key] = {}
            dict_merge(a[key], b[key], path + [str(key)])
        else:
            a[key] = b[key]
    return a
