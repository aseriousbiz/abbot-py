import unittest

from SkillRunner.bot.platform_type import PlatformType
from SkillRunner.bot.users import Users
from SkillRunner.bot.apiclient import ApiClient
from SkillRunner.bot.chat_address import ChatAddress, ChatAddressType

class RoomsTest(unittest.TestCase):
    def test_get_target(self):
        users = Users()
        user = users.get_target("U1234")
        self.assertEqual("U1234", user.id)
        self.assertEqual(
            ChatAddress(ChatAddressType.USER, "U1234"),
            user.get_chat_address()
        )
        self.assertEqual(
            ChatAddress(ChatAddressType.USER, "U1234", "1234.5678"),
            user.get_thread("1234.5678")
        )

if __name__ == '__main__':
    unittest.main()