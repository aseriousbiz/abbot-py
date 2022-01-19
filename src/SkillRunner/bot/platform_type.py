from enum import IntEnum

class PlatformType(IntEnum):
    UNIT_TEST = 0
    SLACK = 1
    DISCORD = 2
    MS_TEAMS = 3
    DIRECT_LINE = 4
    BOT_CONSOLE = 5

    @property
    def name(self):
        return {
            0: 'Unit Test',
            1: 'Slack',
            2: 'Discord',
            3: 'Microsoft Teams',
            4: 'Direct Line',
            5: 'Bot Console'
        }.get(self.value)

    @classmethod
    def parse(cls, val):
        if val is None:
            return PlatformType.UNIT_TEST

        if isinstance(val, str):
            return {
                'unittest': cls.UNIT_TEST,
                'slack': cls.SLACK,
                'discord': cls.DISCORD,
                'msteams': cls.MS_TEAMS,
                'directline': cls.DIRECT_LINE,
                'botconsole': cls.BOT_CONSOLE,
            }.get(val.lower())
        return cls(val)
