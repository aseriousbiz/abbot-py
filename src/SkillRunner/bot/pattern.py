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
        self.pattern_type = PatternType.parse(request.get('PatternType'))
        self.pattern = request.get('Pattern')
        self.case_sensitive = request.get('CaseSensitive')


    def __str__(self):
        return f'{self.pattern_type.name} `{self.pattern}` (case sensitive: {self.case_sensitive})'

    def __eq__(self, other):
        return self.name == other.name and \
            self.description == other.description and \
            self.pattern_type == other.pattern_type and \
            self.pattern == other.pattern and \
            self.case_sensitive == other.case_sensitive


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
    
    @classmethod
    def parse(cls, val):
        if val is None:
            return PatternType.NONE

        if isinstance(val, str):
            return {
                'none': cls.NONE,
                'startswith': cls.STARTS_WITH,
                'endswith': cls.ENDS_WITH,
                'contains': cls.CONTAINS,
                'regularexpression': cls.REGULAR_EXPRESSION,
                'exactmatch': cls.EXACT_MATCH,
            }.get(val.lower())

        return cls(val)