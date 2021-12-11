import unittest

from SkillRunner.bot.platform_type import PlatformType
from SkillRunner.bot.users import Users
from SkillRunner.bot.apiclient import ApiClient
from SkillRunner.bot.conversation_address import ConversationAddress, ConversationType

class RoomsTest(unittest.TestCase):
    def test_get_conversation(self):
        users = Users()
        user = users.get_conversation("U1234")
        self.assertEqual("U1234", user.id)
        self.assertEqual(
            ConversationAddress(ConversationType.USER, "U1234"),
            user.get_conversation_address()
        )
        self.assertEqual(
            ConversationAddress(ConversationType.USER, "U1234", "1234.5678"),
            user.get_thread("1234.5678")
        )

if __name__ == '__main__':
    unittest.main()