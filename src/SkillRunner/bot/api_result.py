class ApiResult(object):
    """
    A class to represent the result of an API call.
    """
    def __init__(self, response):
        self.ok = response.get('ok', False)
        """ Whether the operation succeeded. """
        self.error = response.get('error', None)
        """ The error message if the operation failed. """
