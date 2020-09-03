import sys
import logging
import json
import traceback
import os # used to block environ access

import azure.functions as func
from __app__.SkillRunner import bot as _bot
from __app__.SkillRunner import exceptions


def run_code(req, api_token):
    # Instantiate a bot object
    try:
        bot = _bot.Bot(req, api_token)
        bot.run_user_script()
        return bot.__ScriptResponse__
        logging.warning("hi there")
    except Exception as e:
        raise e
    

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
        logging.info(json.dumps(e, cls=exceptions.ExceptionEncoder))
        exception = e
        response = json.dumps([e], cls=exceptions.ExceptionEncoder)
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
    except exceptions.InterpreterError as e:
        exception = e
        response = json.dumps([e], cls=exceptions.ExceptionEncoder)
        return func.HttpResponse(
            body=response,
            mimetype="text/json",
            status_code=500
        )
    except Exception as e: 
        response = json.dumps([{ "errorId": type(e).__name__, "description": str(e) }])
        logging.warning(response)
        return func.HttpResponse(
            body=response,
            mimetype="text/json",
            status_code=500
        )