import unittest

from SkillRunner.bot.platform_type import PlatformType
from SkillRunner.bot.bot import Bot
from SkillRunner.bot.mention import Mention, TimeZone
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
TEST_SEND_USER = Mention("U777", "cloud", "Cloud Strife", "cstrife@ava.lanche", "Midgar", TimeZone("MST"))
TEST_SEND_ROOM = Room("C777", "#midgar")


class BotRepliesTest(unittest.TestCase):
    def test_read_conversation_from_SkillInfo(self):
        bot = self.create_test_bot({
            "SkillInfo": {
                "Conversation": {
                    "Id": "42"
                }
            }
        })
        self.assertEqual("42", bot.conversation.id)

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
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                dict_merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a