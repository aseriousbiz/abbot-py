import unittest

from SkillRunner.bot.mention import Mention, TimeZone
from SkillRunner.bot.chat_address import ChatAddress, ChatAddressType

TEST_SEND_USER = Mention(1, "cloud", "Cloud Strife", "cstrife@ava.lanche", "Midgar", TimeZone("MST"))

class MentionTest(unittest.TestCase):
    def test_get_chat_address(self):
        self.assertEqual(
            ChatAddress(ChatAddressType.USER, TEST_SEND_USER.id),
            TEST_SEND_USER.get_chat_address()
        )

    def test_get_thread(self):
        self.assertEqual(
            ChatAddress(ChatAddressType.USER, TEST_SEND_USER.id, "1234.5678"),
            TEST_SEND_USER.get_thread("1234.5678")
        )

if __name__ == '__main__':
    unittest.main()