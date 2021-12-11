import unittest
from SkillRunner.bot.conversation_address import ConversationAddress, ConversationType

from SkillRunner.bot.room import Room

TEST_SEND_ROOM = Room(1, "#midgar")

class RoomTest(unittest.TestCase):
    def test_get_conversation_address(self):
        self.assertEqual(
            ConversationAddress(ConversationType.ROOM, TEST_SEND_ROOM.id),
            TEST_SEND_ROOM.get_conversation_address()
        )

    def test_get_thread(self):
        self.assertEqual(
            ConversationAddress(ConversationType.ROOM, TEST_SEND_ROOM.id, "1234.5678"),
            TEST_SEND_ROOM.get_thread("1234.5678")
        )

if __name__ == '__main__':
    unittest.main()