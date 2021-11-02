class SignalEvent(object):
    """
    A signal raised by a skill or pattern.
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
        self._signal_message = signal_source_message.get('SignalEvent')
        self._signal_event = None


    @property
    def signal_event(self):
        if self._signal_event is None and self._signal_message is not None:
            signal_event = self._signal_message.get('SignalEvent')
            self._signal_event = SignalEvent(signal_event) if signal_event is not None else None
        return self._signal_event


class RootSourceSkill(SignalSource):
    """
    Information about the root source skill that raised a signal.
    """
    def __init__(self, root_source_message):
        super().__init__(root_source_message)
        self.request = root_source_message.get('Request')
        self.is_request = root_source_message.get('IsRequest')
        self.is_interaction = root_source_message.get('IsInteraction')
        self.is_chat = root_source_message.get('IsChat')
        self.is_pattern_match = root_source_message.get('IsPatternMatch')
        self.pattern = root_source_message.get('Pattern')