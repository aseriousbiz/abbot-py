
import unittest

from typing import Union
from parameterized import parameterized

from SkillRunner.bot.pattern import Pattern, PatternType

class PatternTest(unittest.TestCase):
    @parameterized.expand([
        ("numeric_type", {
            "Name": "test",
            "Description": "desc",
            "PatternType": PatternType.CONTAINS,
            "Pattern": "P",
            "CaseSensitive": True
        }, Pattern({
            "Name": "test",
            "Description": "desc",
            "PatternType": PatternType.CONTAINS,
            "Pattern": "P",
            "CaseSensitive": True
        })),
        ("string_type", {
            "Name": "test",
            "Description": "desc",
            "PatternType": "Contains",
            "Pattern": "P",
            "CaseSensitive": True
        }, Pattern({
            "Name": "test",
            "Description": "desc",
            "PatternType": PatternType.CONTAINS,
            "Pattern": "P",
            "CaseSensitive": True
        }))
    ])
    def test_parse(self, name: str, json: dict, pattern: Pattern):
        self.assertEqual(pattern, Pattern(json))