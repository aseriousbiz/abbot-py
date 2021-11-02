from enum import IntEnum

class Pattern(object):
    """
    The pattern that caused a skill to be invoked. Most skills are called by name. For example, by mentioning
    Abbot followed by the skill name, or by using the shortcut character followed  by the skill name. For
    example, `.help` calls the `help` skill.

    A pattern is another way a skill can be called. When a message that is NOT an Abbot command matches a
    skill's pattern, the skill is called with the message as the arguments. This interface describes such a
    pattern.
    """
    def __init__(self, request):
        self.name = request.get('Name')
        self.description = request.get('Description')
        self.pattern_type = PatternType(request.get('PatternType'))
        self.pattern = request.get('Pattern')
        self.case_sensitive = request.get('CaseSensitive')


    def __str__(self):
        return f'{self.pattern_type.name} `{self.pattern}` (case sensitive: {self.case_sensitive})'


class PatternType(IntEnum):
    NONE = 0
    STARTS_WITH = 1
    ENDS_WITH = 2
    CONTAINS = 3
    REGULAR_EXPRESSION = 4
    EXACT_MATCH = 5

    @property
    def name(self):
        return {
            0: 'None',
            1: 'Starts With',
            2: 'Ends With',
            3: 'Contains',
            4: 'Regular Expression',
            5: 'Exact Match'
        }.get(self.value)