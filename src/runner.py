# A standalone server for the Python skill runner,
# designed to run anywhere a docker container can run.
# Authentication takes place using a single shared secret
# in the environment variable ABBOT_SKILL_RUNNER_TOKEN

import json
import os
import logging
from SkillRunner.bot.bot import Bot

from flask import Flask,redirect,request,Response

secret = os.environ.get("ABBOT_SKILL_RUNNER_TOKEN")
if secret is None:
    raise Exception("ABBOT_SKILL_RUNNER_TOKEN environment variable not set")

env = os.environ.get("ABBOT_ENV", "production")
if env == "dev":
    Flask.debug = True
if len(secret) < 64 and env != "dev":
    raise Exception("ABBOT_SKILL_RUNNER_TOKEN is too short")

app = Flask(__name__)

my_path = os.path.realpath(__file__)
branch_info_path = os.path.join(my_path, "build_info.txt")

branch_info = { "branch": "unknown", "sha": "unknown" }

# pylint: disable=bare-except
try:
    with open(branch_info_path, "r", encoding='utf-8') as f:
        lines = f.readlines()
        branch_info["branch"] = lines[0]
        branch_info["sha"] = lines[1]
except:
    # Ignore all failures
    branch_info = { "branch": "<unknown>", "sha": "<unknown>" }
# pylint: enable=bare-except

@app.route("/")
def index():
    """
    The root URL, just redirects to the status endpoint
    """
    return redirect("/api/v1/status")

@app.route("/api/v1/status", methods=["GET"])
def status():
    """
    Returns the current status of the application
    """
    return {
        "status": "ok",
        "branch": branch_info["branch"],
        "sha": branch_info["sha"],
    }

def get_token():
    """
    Retrieves the auth token from either the Authorization header or the 'code' query string parameter
    (The latter of which is intended only to emulate Azure Functions)
    """
    auth_header = request.headers.get("Authorization")
    if auth_header is not None:
        splat = auth_header.split(' ')
        if len(splat) == 2 and splat[0] == "Bearer":
            app.logger.debug("Using 'Authorization' header to authenticate")
            return splat[1]
    code = request.args.get('code')
    if code is not None:
        app.logger.debug("Using 'code' query string value to authenticate")
        return code

@app.route("/api/v1/execute", methods=["POST"])
def execute():
    """
    Executes skill code
    """

    # Authenticate using either a Bearer token, or the 'code' parameter
    token = get_token()
    if token != secret:
        app.logger.debug("Request does not contain a token")
        return Response("Access Denied", status = 401)

    body = request.json
    api_token = request.headers.get('x-abbot-skillapitoken')
    trace_parent = request.headers.get('traceparent')

    bot = Bot(body, api_token, trace_parent, app.logger.getChild('Bot'))
    app.logger.debug("Running user skill")
    bot.run_user_script()

    response = {
        "success": True,
    }
    if bot.is_request:
        response.Content = bot.response.raw_content
        response.ContentType = bot.response.content_type
        headers = {}
        for key, value in bot.response.headers.items():
            headers[key] = [value]
        response.Headers = headers

    return Response(json.dumps(response), mimetype="application/vnd.abbot.v1+json")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9001))
    host = os.environ.get("HOST", "127.0.0.1")
    app.run(host=host, port=port)