import sys
import logging
import json
import traceback

import azure.functions as func


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


def run_code(code, command):
    try:
        response = "no response was previded"
        script_locals = {"command": command}
        exec(code, globals(), script_locals)
        return script_locals['response']
    except SyntaxError as e:
        description = "{}: {}".format(e.__class__.__name__, e.args[0])
        err = InterpreterError("SyntaxError", description, e.lineno, 0)
        raise err

    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        tb = traceback.TracebackException(exc_type, exc_value, exc_tb)

        try:
            line_number = tb.lineno
        except:
            line_number = 0

        try:
            offset = tb.offset
        except:
            offset = 0

        err = InterpreterError(str(e.__class__.__name__), str(exc_value), line_number, offset)
        raise err


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("In the Python Function Runner")
    logging.info(dir(req))
    logging.info("json:")
    logging.info(req.get_json())
    logging.info("body")
    logging.info(req.get_body())
    logging.info("params")
    logging.info(req.params)

    req_body = req.get_json()
    code = req_body.get('Code')
    command = req_body.get('Arguments')


    if not command:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            command = req_body.get('command')
            code = req_body.get('code')

    if command:
        try:
            result = run_code(code, command)
            logging.info("responding with: ")
            response = json.dumps([result])
            logging.info(response)
            return func.HttpResponse(
                body=response,
                mimetype="text/json",
                status_code=200
            )
        except InterpreterError as e:
            logging.info(json.dumps(e, cls=ExceptionEncoder))
            return func.HttpResponse(
                body=json.dumps(e, cls=ExceptionEncoder),
                mimetype="text/json",
                status_code=500
            )
    else:
        return func.HttpResponse(
             "You didn't enter a command...",
             status_code=200
        )
