import logging
import json
import jsonpickle
import os 

import azure.functions as func

from .bot import bot as _bot
from .bot import exceptions
from .bot.bot import Button
from .bot.arguments import Argument, MentionArgument, RoomArgument
from .bot.pattern import PatternType
from .bot.utils import Environment

import nltk

MIN_CORPORA = [
    'brown',  # Required for FastNPExtractor
    'punkt',  # Required for WordTokenizer
    'wordnet',  # Required for lemmatization
    'averaged_perceptron_tagger',  # Required for NLTKTagger
]

if not Environment.is_test():
    # Download the minimum corpora required for NLTK / TextBlob
    for corpora in MIN_CORPORA:
        nltk.download(corpora)

class ResponseManager:
    def __init__(self):
        self.ContentType = None
        self.Content = None
        self.Success = True
        self.Errors = []
        self.Replies = []
        self.Headers = None

    def add(self, message):
        self.Replies.append(message)

    def addError(self, error):
        self.Errors.append(error)
        self.Success = False


def run_code(req, api_token, trace_parent):
    # Instantiate a bot object
    try:
        bot = _bot.Bot(req, api_token, trace_parent)
        bot.run_user_script()
        return bot
    except Exception as e:
        raise e
    

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Allow Debug logs through, Azure Functions will filter further
    logging.Logger.root.level = 10

    rm = ResponseManager()

    func_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    branch_info_path = os.path.join(func_root, "branch_info.txt")

    branch_info = { "branch": "unknown", "sha": "unknown" }
    try:
        with open(branch_info_path, "r") as f:
            lines = f.readlines()
            branch_info["branch"] = lines[0]
            branch_info["sha"] = lines[1]
    except:
        # Ignore failures
        pass

    if req.method == "GET":
        branch = branch_info["branch"]
        sha = branch_info["sha"]
        msg = f"Ok! Running Abbot Python Runner v0.10.2 from {branch} branch at {sha}"
        rm.add(msg)
        return func.HttpResponse(
            body=jsonpickle.encode(rm, unpicklable=False),
            mimetype="application/vnd.abbot.v1+json",
            status_code=200
        )

    try:
        req_body = req.get_json()
        # The token is necessary for using the data API
        api_token = req.headers.get('x-abbot-skillapitoken')
        trace_parent = req.headers.get('traceparent')
        bot = run_code(req_body, api_token, trace_parent)
        for response in bot.responses:
            rm.add(response)
        if bot.is_request:
            response = bot.response
            rm.Content = response.raw_content
            rm.ContentType = response.content_type
            headers = {}
            for key, value in response.headers.items():
                headers[key] = [value]
            rm.Headers = headers

            logging.info("rm: ")
            logging.info(jsonpickle.encode(rm))

    except exceptions.InterpreterError as e:
        rm.addError(e)
    except Exception as e: 
        logging.error(e)
        rm.addError({ "errorId": type(e).__name__, "description": str(e) })
    finally:
        if rm.Success:
            status_code=200
        else:
            status_code=500

        return func.HttpResponse(
            body=jsonpickle.encode(rm, unpicklable=False),
            mimetype="application/vnd.abbot.v1+json",
            status_code=status_code
        )
