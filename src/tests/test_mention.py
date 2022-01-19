import unittest

from parameterized import parameterized

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
    
    # We try _real_ hard to parse TimeZone info :)
    # It should be consistent from now on, but we need to handle old code for a bit.
    # Also, the behavior when multiple TimeZone values are set in multiple places is undefined. Even old code shouldn't do that anyway.
    @parameterized.expand([
        ("timezone_id_at_root", { "Id": "U123", "TimeZoneId": "America/Vancouver" }, TimeZone("America/Vancouver")),
        ("timezone_id_in_location", { "Id": "U123", "Location": { "TimeZoneId": "America/Vancouver" } }, TimeZone("America/Vancouver")),
        ("timezone_at_root", { "Id": "U123", "TimeZone": "America/Vancouver" }, TimeZone("America/Vancouver")),
        ("timezone_in_location", { "Id": "U123", "Location": { "TimeZone": "America/Vancouver" } }, TimeZone("America/Vancouver")),
        ("timezone_obj_at_root", { "Id": "U123", "TimeZone": { "Id": "America/Vancouver", "MinOffset": 1, "MaxOffset": 2 } }, TimeZone("America/Vancouver", 1, 2)),
        ("timezone_obj_in_location", { "Id": "U123", "Location": { "TimeZone": { "Id": "America/Vancouver", "MinOffset": 1, "MaxOffset": 2 } } }, TimeZone("America/Vancouver", 1, 2)),
    ])
    def test_from_json(self, name: str, json: dict, tz: TimeZone):
        mention = Mention.from_json(json)
        self.assertEqual(tz, mention.timezone)
        self.assertEqual(tz, mention.location.timezone)

if __name__ == '__main__':
    unittest.main()