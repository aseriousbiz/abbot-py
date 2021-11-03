import json
import jsonpickle
from types import SimpleNamespace

class TriggerEvent(object):
    """
    A request triggered by an external event.

    :var content_type: The Content Type of the request.
    :var http_method: The Http Method of the request.
    :var is_form: True if the request is a form. Otherwise False.
    :var is_json: True if the request contains json data. Otherwise False.
    :var headers: The request headers.
    :var form: Form data, if it exists.
    :var query: QueryString data, if it exists.
    :var url: The request url.
    :var raw_body: The raw body of the request.
    """
    def __init__(self, request):
        self.content_type = request.get('ContentType')
        self.http_method = request.get('HttpMethod')
        self.is_form = request.get('IsForm')
        self.is_json = request.get('IsJson')
        self.headers = request.get('Headers')
        self.form = request.get('Form')
        self.query = request.get('Query')
        self.url = request.get('Url')
        self.raw_body = request.get('RawBody')

    def json(self):
        return json.loads(self.raw_body, object_hook=lambda d: SimpleNamespace(**d))

    def toJSON(self):
        return jsonpickle.encode(self)
