import json
import unittest

from SkillRunner.bot.chat_address import ChatAddress, ChatAddressType

class ChatAddressTest(unittest.TestCase):
    def test_toJSON(self):
        addr = ChatAddress(ChatAddressType.USER, "U1234")
        j = json.dumps(addr.toJSON())
        self.assertEqual(j, '{"Type": 0, "Id": "U1234"}')
    
    def test_toJSON_thread_id(self):
        addr = ChatAddress(ChatAddressType.USER, "U1234", "123.456")
        j = json.dumps(addr.toJSON())
        self.assertEqual(j, '{"Type": 0, "Id": "U1234", "ThreadId": "123.456"}')
    
    def test_get_chat_address_returns_self(self):
        addr = ChatAddress(ChatAddressType.USER, "U1234")
        self.assertEqual(addr, addr.get_chat_address())

if __name__ == '__main__':
    unittest.main()