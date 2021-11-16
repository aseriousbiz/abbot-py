import logging
import jsonpickle
import os 

import azure.functions as func

from .bot import bot as _bot
from .bot import exceptions
from .bot.bot import Button
from .bot.arguments import Argument, MentionArgument, RoomArgument
from .bot.pattern import PatternType

import nltk

MIN_CORPORA = [
    'brown',  # Required for FastNPExtractor
    'punkt',  # Required for WordTokenizer
    'wordnet',  # Required for lemmatization
    'averaged_perceptron_tagger',  # Required for NLTKTagger
]

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


def deny_os_modules():
    """
    There are some modules in `os` that user scripts should not run.
    Denying these prevents anything in the runner from using them.
    """
    deny = [
    '_execvpe', 'chmod', 'chown', 'chroot', 'execl', 'execle', 'execlp', 'execlpe', 'execv', 'execve', 'execvp', 
    'execvpe', 'kill', 'killpg', 'lchmod', 'lchown', 'link', 'posix_spawn', 'posix_spawnp','spawnl', 'spawnle', 
    'spawnlp', 'spawnlpe', 'spawnv', 'spawnve', 'spawnvp', 'spawnvpe', 'symlink']

    for attr, value in os.__dict__.items():
        if attr in deny:
            setattr(os, attr, lambda self: PermissionError("Access to this module (os.{}) is denied".format(attr)))    


def run_code(req, api_token, trace_parent):
    # Instantiate a bot object
    try:
        bot = _bot.Bot(req, api_token, trace_parent)
        bot.run_user_script()
        return bot
    except Exception as e:
        raise e
    

def main(req: func.HttpRequest) -> func.HttpResponse:
    rm = ResponseManager()

    if req.method == "GET":
        rm.add("Ok! Running Abbot Python Runner v0.10.1.")

    try:
        deny_os_modules()
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
            body=jsonpickle.encode(rm),
            mimetype="application/vnd.abbot.v1+json",
            status_code=status_code
        )
