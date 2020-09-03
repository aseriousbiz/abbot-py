import json 
import logging

class ExceptionEncoder(json.JSONEncoder):
    def default(self, o):
        if o.__dict__: 
            return o.__dict__
        else:
            return {"errorId": type(o), "description": str(o)}


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