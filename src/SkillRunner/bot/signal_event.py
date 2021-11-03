from .pattern import Pattern
from .trigger_event import TriggerEvent

class SignalEvent(object):
    """
    A signal raised by a skill.
    """
    def __init__(self, signal_message):
        self._signal_message = signal_message
        self.name = signal_message.get('Name')
        self.arguments = signal_message.get('Arguments')
        self.args = self.arguments
        self._source = None
        self._root_source = None


    @property
    def source(self):
        if self._source is None:
            self._source = SourceSkill(self._signal_message.get('Source'))

        return self._source


    @property
    def root_source(self):
        if self._root_source is None:
            self._root_source = self.__get_root_source()
        return self._root_source


    def __get_root_source(self):
        source = self._signal_message.get('Source')
        while source.get('SignalEvent') is not None:
            source = source.get('SignalEvent').get('Source')

        return RootSourceSkill(source)


class SignalSource(object):
    """
    Information about the source of a signal.
    """
    def __init__(self, signal_source_message):
        self.skill_name = signal_source_message.get('SkillName')
        self.skill_url = signal_source_message.get('SkillUrl')
        self.arguments = signal_source_message.get('Arguments')
        self.args = self.arguments
        self.mentions = signal_source_message.get('Mentions')


class SourceSkill(SignalSource):
    """
    Information about the source skill that raised a signal.
    """
    def __init__(self, signal_source_message):
        super().__init__(signal_source_message)
        self._signal_event_message = signal_source_message.get('SignalEvent')
        self._signal_event = None


    @property
    def signal_event(self):
        if self._signal_event is None and self._signal_event_message is not None:
            self._signal_event = SignalEvent(self._signal_event_message)
        return self._signal_event


class RootSourceSkill(SignalSource):
    """
    Information about the root source skill that raised a signal.
    """
    def __init__(self, root_source_message):
        super().__init__(root_source_message)
        request = root_source_message.get('Request')
        self.request = TriggerEvent(request) if request is not None else None
        self.is_request = root_source_message.get('IsRequest')
        self.is_interaction = root_source_message.get('IsInteraction')
        self.is_chat = root_source_message.get('IsChat')
        self.is_pattern_match = root_source_message.get('IsPatternMatch')
        pattern = root_source_message.get('Pattern')
        self.pattern = Pattern(pattern) if pattern is not None else None