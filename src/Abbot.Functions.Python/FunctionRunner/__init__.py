import sys
import logging
import json
import traceback
import os # used to block environ access

import azure.functions as func
from __app__.FunctionRunner import storage 

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


def run_code(code, arguments, skill_id, user_id, api_token):
    try:
        # Instantiate a brain for persistence
        brain = storage.Brain(skill_id, user_id, api_token)

        # Remove `os` from `sys` so users cannot use the module.
        os_copy = os
        sys.modules['os'] = None
        script_locals = {"args": arguments, "brain": brain}

        # Run the code
        exec(code, script_locals, script_locals)

        # Restore `os` so our code can use it if necessary.
        sys.modules['os'] = os_copy
        
        return script_locals['response']
    except SyntaxError as e:
        description = "{}: {}".format(e.__class__.__name__, e.args[0])
        err = InterpreterError("SyntaxError", description, e.lineno, 0)
        raise err
    except KeyError as e:
        if not script_locals.get('response'):
            err = InterpreterError("NoResponseError", "You must set a value called 'response' in your script.", 0, 0)
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
        code = req_body.get('Code')
        command = req_body.get('Arguments')
        skill_id = req_body.get('SkillId')
        user_id = req_body.get('UserId')

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
        result = run_code(code, command, skill_id, user_id, api_token)
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
