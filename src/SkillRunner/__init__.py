import sys
import logging
import json
import jsonpickle
import traceback
import os # used to block environ access

import azure.functions as func

from .bot import bot as _bot
from .bot import exceptions

class ResponseManager:
    def __init__(self):
        self.content_type = "application/json"
        self.content = None
        self.success = True
        self.errors = []
        self.replies = []
        self.headers = None
    
    def add(self, message):
        self.replies.append(message)
    
    def addError(self, error):
        self.errors.append(error)
        self.success = False
    

def run_code(req, api_token):
    # Instantiate a bot object
    try:
        bot = _bot.Bot(req, api_token)
        bot.run_user_script()
        return bot.responses
    except Exception as e:
        raise e
    

def main(req: func.HttpRequest) -> func.HttpResponse:
    rm = ResponseManager()

    if req.method == "GET":
        rm.add("Ok! Running Abbot Python Runner v0.2.1.")

    try:
        req_body = req.get_json()
        # The token is necessary for using the data API
        api_token = req.headers.get('x-abbot-skillapitoken')
    except Exception as e:
        rm.addError(e)

    try:
        responses = run_code(req_body, api_token)
        for response in responses:
            rm.add(response)
    except exceptions.InterpreterError as e:
        rm.addError(e)
    except Exception as e: 
        rm.addError({ "errorId": type(e).__name__, "description": str(e) })

    finally:
        if rm.success:
            status_code=200
        else:
            status_code=500

        return func.HttpResponse(
            body=jsonpickle.encode(rm),
            mimetype="application/vnd.abbot.v1+json",
            status_code=status_code
        )