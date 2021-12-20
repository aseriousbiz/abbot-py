import unittest

from SkillRunner.bot.platform_type import PlatformType
from SkillRunner.bot.rooms import Rooms
from SkillRunner.bot.apiclient import ApiClient
from SkillRunner.bot.chat_address import ChatAddress, ChatAddressType

class RoomsTest(unittest.TestCase):
    def test_get_target(self):
        rooms = Rooms(ApiClient(42, None, None, None, None), PlatformType.UNIT_TEST)
        room = rooms.get_target("C1234")
        self.assertEqual("C1234", room.id)
        self.assertEqual(
            ChatAddress(ChatAddressType.ROOM, "C1234"),
            room.get_chat_address()
        )
        self.assertEqual(
            ChatAddress(ChatAddressType.ROOM, "C1234", "1234.5678"),
            room.get_thread("1234.5678")
        )

if __name__ == '__main__':
    unittest.main()