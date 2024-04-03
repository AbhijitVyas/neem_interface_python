#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_restful import Api
import ast
import argparse
from neemdata import NEEMData

app = Flask(__name__)
api = Api(app)
neem_data = NEEMData()

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

    print('sub action %s with start time %s and endtime %s', sub_action_type, start_time, end_time)
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
    response = neem_data.add_additional_pouring_information(**request.json)
    return (jsonify(response), 200 if response else 400)

@app.route("/knowrob/api/v1.0/create_episode", methods = ['GET', 'POST'])
def create_episode():
    game_participant = request.json['game_participant']
    game_start_time = request.json['game_start_time']
    print("create an episode with game_participant: %s " %(game_participant))
    NEEMData().create_actor_by_given_name(game_participant)
    print("create an episode with game_Start_time: %s " % (game_start_time))
    response = NEEMData().create_episode(game_participant, game_start_time)
    return (jsonify(response), 200 if response else 400)


@app.route("/knowrob/api/v1.0/finish_episode", methods = ['GET', 'POST'])
def post_finish_episode():
    episode_iri = request.json['episode_iri']
    game_end_time = request.json['game_end_time']
    print("finish an episode with iri: %s " %(episode_iri))
    print("finish an episode with game_Stop_time: %s " % (game_end_time))
    response = NEEMData().finish_episode(episode_iri, game_end_time)
    return (jsonify(response), 200 if response else 400)

# @app.route("/knowrob/api/v1.0/hand_participate", methods = ['GET', 'POST'])
# def post_finish_episode():
#     hand_type = request.json['hand_type']
#     response = NEEMData().hand_participate_in_action(hand_type)
#     if response is not None:
#         return jsonify(response), 200
#     else:
#         return jsonify(response), 400

def startup(host, debug, port):
    app.run(host,debug, port)
    return app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="RESTClient", description="Starts the REST Server to interface with ROSProlog.")
    parser.add_argument('--host', type=str, default="0.0.0.0", help="IP Address for the server.")
    parser.add_argument('--nodebug', action="store_false",help="Do not run the server in debug mode")
    parser.add_argument('--port', type=int, default=8000, help="Port that the server listens on.")
    args = parser.parse_args()
    startup(host=args.host,debug=args.nodebug, port=args.port)