import unittest

from typing import Union
from parameterized import parameterized

from SkillRunner.bot.platform_type import PlatformType

class PlatformTypeTest(unittest.TestCase):
    @parameterized.expand([
        ("DISCORD", PlatformType.DISCORD),
        ("dIsCoRd", PlatformType.DISCORD),
        ("discord", PlatformType.DISCORD),
        (2, PlatformType.DISCORD),
    ])
    def test_parse(self, s: Union[str, int], v: PlatformType):
        self.assertEqual(v, PlatformType.parse(s))