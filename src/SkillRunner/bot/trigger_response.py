import jsonpickle

class TriggerResponse(object):
    """
    A response to an HTTP request triggered by an external event.

    :var raw_content: The raw content to return as the body of the response. Cannot be set if content is set.
    :var content: The content to return as the body of the response. This will be serialized as JSON. Cannot be set if raw_content is set.
    :var content_type: The Content Type of the response. If null, Abbot will choose the best content type using content negotiation.
    :var headers: The request Headers as defined in RFC 2616 that should be sent in the response.
    """
    def __init__(self):
        self.headers = {}
        self._content = None
        self._raw_content = None
        self._content_type = None

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value
        self._raw_content = str(jsonpickle.encode(value))

    @content.deleter
    def content(self):
        del self._content

    @property
    def raw_content(self):
        return self._raw_content

    @raw_content.setter
    def raw_content(self, value):
        self._content = None
        self._raw_content = value if type(value) == str else str(value)

    @raw_content.deleter
    def raw_content(self):
        del self._raw_content

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        self._content_type = value

    @content_type.deleter
    def content_type(self):
        del self._content_type