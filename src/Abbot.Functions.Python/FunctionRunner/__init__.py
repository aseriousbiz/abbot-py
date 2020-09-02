import sys
import logging
import json
import traceback
import os # used to block environ access

import azure.functions as func
from __app__.FunctionRunner import bot as _bot

class ExceptionEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class InterpreterError(Exception): 
    def __init__(self, name, description, line_number, offset):
        self.errorId = name
        self.lineStart = line_number
        self.lineEnd = line_number
        self.spanStart = offset
        self.spanEnd = offset+1
        self.description = description
    
    def __str__(self):
        return "{} at line {}, character {}".format(self.description, self.lineStart, self.spanStart)


def run_code(req, api_token):
    try:
        # Instantiate a bot object
        bot = _bot.Bot(req, api_token)
        code = req.get('Code')

        # Remove `os` from `sys` so users cannot use the module.
        os_copy = os
        sys.modules['os'] = None
        script_locals = {"bot": bot, "__ScriptResponse__": None}

        # Run the code
        exec(code, script_locals, script_locals)

        # Restore `os` so our code can use it if necessary.
        sys.modules['os'] = os_copy
        logging.info("Script Locals:")
        logging.info(script_locals)
        return script_locals['__ScriptResponse__']
    except SyntaxError as e:
        description = "{}: {}".format(e.__class__.__name__, e.args[0])
        err = InterpreterError("SyntaxError", description, e.lineno, 0)
        raise err
    except KeyError as e:
        if not script_locals.get('__ScriptResponse__') or script_locals.get('__ScriptResponse__') is None:
            err = InterpreterError("NoResponseError", "You must call `bot.reply(<output>)` with your output.", 0, 0)
            raise err
        else:
            pass
    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        tb = traceback.TracebackException(exc_type, exc_value, exc_tb)
        try:
            line_number = tb.lineno
        except:
            line_number = -1

        try:
            offset = tb.offset
        except:
            offset = -1

        err = InterpreterError(str(e.__class__.__name__), str(exc_value), line_number, offset)
        raise err


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("In the Python Function Runner")
    if req.method == "GET":
        return func.HttpResponse(
            body=json.dumps(["Ok!"]),
            mimetype="text/json",
            status_code=200
        )

    try:
        req_body = req.get_json()
        # The token is necessary for using the data API
        api_token = req.headers.get('x-abbot-skillapitoken')
    except Exception as e:
        logging.info(json.dumps(e, cls=ExceptionEncoder))
        exception = e
        response = json.dumps([e], cls=ExceptionEncoder)
        return func.HttpResponse(
            body=json.dumps(["Not a valid request"]),
            mimetype="text/json",
            status_code=500
        )

    try:
        result = run_code(req_body, api_token)
        response = json.dumps([result])
        return func.HttpResponse(
            body=response,
            mimetype="text/json",
            status_code=200
        )
    except InterpreterError as e:
        logging.info(json.dumps(e, cls=ExceptionEncoder))
        exception = e
        response = json.dumps([e], cls=ExceptionEncoder)
        return func.HttpResponse(
            body=response,
            mimetype="text/json",
            status_code=500
        )
