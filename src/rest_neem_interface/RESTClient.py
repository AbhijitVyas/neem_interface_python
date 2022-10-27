#!/usr/bin/env python3
import os
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import pandas as pd
from .neemdata import NEEMData

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)
api = Api(app)


@app.route("/")
def get_hello_world():
    return "Hello, World!"


@app.route("/load_neem_to_kb")
def get_neem_to_load_into_kb():
    response = NEEMData().load_neem_to_kb()
    if response is not None:
        return jsonify("successfully restored neem to mongodb"), 200
    else:
        return jsonify(response), 400

# not working at the moment
#@app.route("/clear_kb")
#def clear_knowledge_base():
#    response = NEEMData().clear_beliefstate()
#    if response is not None:
#        return jsonify("successfully wiped-out mongodb kb"), 200
#    else:
#        return jsonify(response), 400


@app.route("/get_all_actions")
def get_all_actions():
    response = NEEMData().get_all_actions()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_all_actions_start_time")
def get_all_actions_start_time_stamps():
    response = NEEMData().get_all_actions_start_timestamps()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_all_objects_participates_in_actions")
def get_all_objects_participates_in_actions():
    response = NEEMData().get_all_objects_participates_in_actions()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400