import logging
import jsonpickle
import os 

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
        rm.add("Ok! Running Abbot Python Runner v0.6.1.")

    try:
        deny_os_modules()
        req_body = req.get_json()
        # The token is necessary for using the data API
        api_token = req.headers.get('x-abbot-skillapitoken')
        responses = run_code(req_body, api_token)
        for response in responses:
            rm.add(response)
    except exceptions.InterpreterError as e:
        rm.addError(e)
    except Exception as e: 
        logging.error(e)
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