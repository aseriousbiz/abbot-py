import logging

class SignalEvent(object):
    """
    A signal raised by a skill or pattern.
    """
    def __init__(self, signal_message):
        logging.info(f"SignalEvent.__init__: creating from {signal_message}")
        self._signal_message = signal_message
        self.name = signal_message.get('Name')
        self.arguments = signal_message.get('Arguments')
        self.args = self.arguments
        self._source = None
        self._root_source = None
        logging.info(f"SignalEvent.__init__: created")


    @property
    def source(self):
        logging.info(f"SignalEvent.@source: retrieving.")

        if self._source is None:
            self._source = SourceSkill(self._signal_message.get('Source'))
        logging.info(f"SignalEvent.@source: retrieved.")

        return self._source


    @property
    def root_source(self):
        if self._root_source is None:
            self._root_source = self.__get_root_source()
        return self._root_source


    def __get_root_source(self):
        logging.info(f"__get_root_source: Retrieving self.source")
        source = self._signal_message.get('Source')
        logging.info(f"__get_root_sourceRetrieved self.source")
        while source.get('SignalEvent') is not None:
            source = source.get('SignalEvent').get('Source')

        return RootSourceSkill(source)


class SignalSource(object):
    """
    Information about the source of a signal.
    """
    def __init__(self, signal_source_message):
        logging.info(f"SignalSource.__init__ with source message: {signal_source_message}")
        self.skill_name = signal_source_message.get('SkillName')
        self.skill_url = signal_source_message.get('SkillUrl')
        self.arguments = signal_source_message.get('Arguments')
        self.args = self.arguments
        self.mentions = signal_source_message.get('Mentions')
        logging.info(f"SignalSource.__init__ completed.")


class SourceSkill(SignalSource):
    """
    Information about the source skill that raised a signal.
    """
    def __init__(self, signal_source_message):
        logging.info(f"SourceSkill.__init__ with source message: {signal_source_message}")
        super().__init__(signal_source_message)
        self._signal_message = signal_source_message.get('SignalEvent')
        logging.info(f"SourceSkill.__init__ completed.")
        self._signal_event = None


    @property
    def signal_event(self):
        logging.info(f"SourceSkill.@signal_event: Retrieving signal event")
        if self._signal_event is None and self._signal_message is not None:
            signal_event = self._signal_message.get('SignalEvent')
            self._signal_event = SignalEvent(signal_event) if signal_event is not None else None
        logging.info(f"SourceSkill.@signal_event: Retrieved")
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