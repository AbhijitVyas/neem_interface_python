#!/usr/bin/env python3
import os
from flask import Flask, jsonify, request
from flask_restful import Api
import ast
import argparse
from neemdata import NEEMData
from neem_interface_python.neem_interface import NEEMInterface

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
api = Api(app)
neem_data = NEEMData()

@app.route("/")
def get_hello_world():
    return "Hello, World!"

@app.route("/knowrob/api/v1.0/<string:function>")
def get_neem_data(function):
    response = getattr(neem_data,function)()
    return (jsonify(response), 200 if response else 400)

@app.route("/knowrob/api/v1.0/create_actor_by_given_name", methods = ['GET', 'POST'])
def create_actor_by_given_name():
    actor_name = request.json['actor_name']
    print("actor with given name REST: ", actor_name)
    response = neem_data.create_actor_by_given_name(actor_name)
    return (jsonify(response), 200 if response else 400)

@app.route("/knowrob/api/v1.0/add_subaction_with_task", methods = ['GET', 'POST'])
def post_add_subaction_with_task():
    parent_action_iri = request.json['parent_action_iri']
    sub_action_type = request.json['sub_action_type']
    task_type = request.json['task_type']
    start_time = request.json['start_time']
    end_time = request.json['end_time']
    objects_participated = request.json['objects_participated']
    additional_information = request.json['additional_event_info']
    game_participant = request.json['game_participant']

    # check if the additional_information is of type str and then replace all double quotes with single for json to accept it as dict object
    if(type(additional_information) == str):
        additional_information = additional_information.replace("'", '"')

    additional_information_dict_obj = []
    if additional_information:
        additional_information_dict_obj = ast.literal_eval(additional_information)

    response = neem_data.add_subaction_with_task(parent_action_iri, sub_action_type, task_type, start_time, end_time,
                                                  objects_participated, additional_information_dict_obj, game_participant)
    if response:
        print("Sub task is added to the KB!", response)
    return (jsonify(response), 200 if response else 400)

@app.route("/knowrob/api/v1.0/add_additional_pouring_information", methods = ['GET', 'POST'])
def post_add_additional_pouring_information():
    parent_action_iri = request.json['parent_action_iri']
    sub_action_type = request.json['sub_action_type']
    max_pouring_angle = request.json['max_pouring_angle']
    min_pouring_angle = request.json['min_pouring_angle']
    source_container = request.json['source_container']
    destination_container = request.json['destination_container']
    pouring_pose = request.json['pouring_pose']
    response = neem_data.add_additional_pouring_information(parent_action_iri, sub_action_type, max_pouring_angle, min_pouring_angle, source_container, destination_container, pouring_pose)
    return (jsonify(response), 200 if response else 400)

@app.route("/knowrob/api/v1.0/create_episode", methods = ['GET', 'POST'])
def create_episode():
    game_participant = request.json['game_participant']
    print("create an episode with game_participant: %s " %(game_participant))
    neem_data.create_actor_by_given_name(game_participant)
    response = neem_data.create_episode(game_participant)
    return (jsonify(response), 200 if response else 400)


@app.route("/knowrob/api/v1.0/finish_episode", methods = ['GET', 'POST'])
def post_finish_episode():
    episode_iri = request.json['episode_iri']
    print("finish an episode with iri: %s " %(episode_iri))
    response = neem_data.finish_episode(episode_iri)
    return (jsonify(response), 200 if response else 400)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="RESTClient", description="Starts the REST Server to interface with ROSProlog.")
    parser.add_argument('--host', type=str, default="0.0.0.0", help="IP Address for the server.")
    parser.add_argument('--nodebug', action="store_false",help="Do not run the server in debug mode")
    parser.add_argument('--port', type=int, default=8000, help="Port that the server listens on.")
    args = parser.parse_args()
    app.run(host=args.host,debug=args.nodebug, port=args.port)