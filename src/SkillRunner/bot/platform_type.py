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