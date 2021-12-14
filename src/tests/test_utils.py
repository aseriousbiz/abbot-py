import unittest

from typing import Optional
from parameterized import parameterized

from SkillRunner.bot.conversation_address import ConversationAddress, ConversationType
from SkillRunner.bot.utils import Utilities

class UtilitiesTest(unittest.TestCase):
    @parameterized.expand([
        ("message_in_thread",
            "https://aseriousbiz.slack.com/archives/C012ZJGPYTF/p1639006342178800?thread_ts=1639006311.178500&cid=C012ZJGPYTF",
            ConversationType.ROOM, "C012ZJGPYTF", "1639006311.178500"),
        ("message", 
            "https://aseriousbiz.slack.com/archives/C012ZJGPYTF/p1639006311178500",
            ConversationType.ROOM, "C012ZJGPYTF", "1639006311.178500"),
        ("channel",
            "https://aseriousbiz.slack.com/archives/C012ZJGPYTF",
            ConversationType.ROOM, "C012ZJGPYTF", None),
        ("dm_convo",
            "https://aseriousbiz.slack.com/archives/D02LV16PBE3",
            ConversationType.USER, "D02LV16PBE3", None),
        ("user",
            "https://aseriousbiz.slack.com/team/U02EMN2AYGH",
            ConversationType.USER, "U02EMN2AYGH", None),
    ])
    def test_parse_slack_url(self, name: str, url: str, conv_type: ConversationType, id: str, thread_id: Optional[str]):
        utils = Utilities(None)
        result = utils.parse_slack_url(url)
        self.assertIsNotNone(result)

        addr = result.get_conversation_address()
        self.assertEqual(conv_type, addr.type)
        self.assertEqual(id, addr.id)
        self.assertEqual(thread_id, addr.thread_id)

    def test_parse_invalid_slack_url(self):
        utils = Utilities(None)
        result = utils.parse_slack_url("https://something.discord.example.com")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
