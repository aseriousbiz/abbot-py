import sys
import logging
import json
import traceback
import os # used to block environ access

import azure.functions as func

from .bot import bot as _bot


def run_code(req, api_token):
    # Instantiate a bot object
    try:
        bot = _bot.Bot(req, api_token)
        bot.run_user_script()
        return bot.responses
    except Exception as e:
        raise e
    

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "GET":
        return func.HttpResponse(
            body=json.dumps(["Ok! Running Abbot Python Runner v0.2.1."]),
            mimetype="text/json",
            status_code=200
        )

    try:
        req_body = req.get_json()
        # The token is necessary for using the data API
        api_token = req.headers.get('x-abbot-skillapitoken')
    except Exception as e:
        exception = e
        response = json.dumps([e], cls=exceptions.ExceptionEncoder)
        return func.HttpResponse(
            body=json.dumps(["Not a valid request"]),
            mimetype="text/json",
            status_code=500
        )

    try:
        responses = run_code(req_body, api_token)
        response = json.dumps(responses)
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
        return func.HttpResponse(
            body=response,
            mimetype="text/json",
            status_code=500
        )