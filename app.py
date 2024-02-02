import logging
import json
import os
from sys import stdout

from flask import Flask, jsonify, make_response, request

import miro_team

app = Flask(__name__)
app.logger.setLevel(os.environ.get("LOGGING_LEVEL", "DEBUG"))
logging.basicConfig(stream=stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


MANDATORY_ARGS = {"user", "team", "internal", "ticket"}


@app.route("/", methods=["GET"])
def helloindex():
    """Application Index page

    Returns:
        Response: html intro page, with links to service routes
    """
    return """
    <h1 style='color: red;'>Welcome to Miro Team Mgmt!!</h1>
    
    """


@app.route("/_health")
def ready():
    """Simple health check to confirm app is responding

    Returns:
        Literal: "OK"
    """
    return "OK"


@app.route("/miro_team/create", methods=["POST"])
def miro_create_team() -> dict:
    """Primary endpoint for Miro Team creations

    Arguments:
        data (dict): containing MANDATORY_ARGS ("user", "team", "internal", and "ticket" keys)

    response{json}:
        Status[str]:
            one of the following states: "Success" "Failed"  "Error" "Exception"
        Message[str]:
            Information to the user about the endpoint action
        original_request(optional)[obj]:
            Data passed to application for this request
        Details(optional)[obj]:
            Extra request/response information
    """
    data = request.get_json()
    response = {"message": "Default failure msg", "status": "Failed"}
    if not all([x in data for x in MANDATORY_ARGS]):
        response[
            "message"
        ] = f"Missing required argument(s): {MANDATORY_ARGS.difference(data.keys())}"
        response["status"] = "Error"
        return response
    try:
        module_output = miro_team.process_team_request(data)
        log.info(
            f"""[MIRO TEAM CREATE] request: {data}; module output: {module_output}"""
        )
    except Exception as exce:
        module_output = None
        dir(exce)
        response["message"] = f"Unexpected error occurred: {exce}"
        log.error(exce)
    finally:
        return make_response(jsonify(module_output or response), 200)


if __name__ == "__main__":
    app.run(debug=True)
