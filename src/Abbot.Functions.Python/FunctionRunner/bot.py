import os
import json
import sys
import logging
import traceback

from __app__.FunctionRunner import storage 
from __app__.FunctionRunner import secrets
from __app__.FunctionRunner import exceptions

class Bot(object):
    def __init__(self, req, api_token):
        skill_id = req.get('SkillId')
        user_id = req.get('UserId')
        timestamp = req.get('Timestamp')

        self.args = req.get('Arguments')
        self.code = req.get('Code')
        self.brain = storage.Brain(skill_id, user_id, api_token, timestamp)
        self.secrets = secrets.Secrets(skill_id, user_id, api_token, timestamp)
    
    def run_user_script(self):
        """
        Run the code the user has submitted.
        """
        try:
            # Remove `os` from `sys` so users cannot use the module.
            os_copy = os
            sys.modules['os'] = None

            script_locals = { "bot": self }

            # Run the code
            exec(self.code, script_locals, script_locals)

            # Restore `os` so our code can use it if necessary.
            sys.modules['os'] = os_copy

            out = script_locals.get('bot')
            logging.info(dir(out))
            return out.__ScriptResponse__
        except SyntaxError as e:
            description = "{}: {}".format(e.__class__.__name__, e.args[0])
            err = exceptions.InterpreterError("SyntaxError", description, e.lineno, 0)
            raise err
        except AttributeError as e:
            if not script_locals.get('__ScriptResponse__') or script_locals.get('__ScriptResponse__') is None:
                err = exceptions.InterpreterError("NoResponseError", "You must call `bot.reply(<output>)` with your output.", 0, 0)
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

            err = exceptions.InterpreterError(str(e.__class__.__name__), str(exc_value), line_number, offset)
            raise err

    
    def reply(self, response):
        self.__ScriptResponse__ = response


    def __repr__(self):
        response = "A very nice bot with these features: \n"
        response += "                args: " + self.args + "\n "
        response += "  __ScriptResponse__: " + __ScriptResponse__

        return response