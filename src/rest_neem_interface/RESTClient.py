#!/usr/bin/env python3
import os
from flask import Flask, render_template, jsonify, request
from flask_restful import Resource, Api, reqparse
import pandas as pd
from .neemdata import NEEMData
import json
import ast
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
api = Api(app)


@app.route("/")
def get_hello_world():
    return "Hello, World!"


@app.route("/knowrob/api/v1.0/load_neem_to_kb")
def get_neem_to_load_into_kb():
    response = NEEMData().load_neem_to_kb()
    if response is not None:
        return jsonify("successfully restored neem to mongodb"), 200
    else:
        return jsonify(response), 400


# not working at the moment
# @app.route("/clear_kb")
# def clear_knowledge_base():
#    response = NEEMData().clear_beliefstate()
#    if response is not None:
#        return jsonify("successfully wiped-out mongodb kb"), 200
#    else:
#        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_all_actions")
def get_all_actions():
    response = NEEMData().get_all_actions()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_all_actions_start_time")
def get_all_actions_start_time_stamps():
    response = NEEMData().get_all_actions_start_timestamps()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400

@app.route("/knowrob/api/v1.0/get_all_actions_end_time")
def get_all_actions_end_time_stamps():
    response = NEEMData().get_all_actions_end_timestamps()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400
    
@app.route("/knowrob/api/v1.0/get_all_objects_participates_in_actions")
def get_all_objects_participates_in_actions():
    response = NEEMData().get_all_objects_participates_in_actions()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


# this method will not return any pose since knowrob tf_get_pose has some bug and does not return any value at the 
#  moment 
@app.route("/knowrob/api/v1.0/get_handpose_at_start_of_action")
def get_handpose_at_start_of_action():
    response = NEEMData().get_handpose_at_start_of_action()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_source_container_while_grasping")
def get_source_container_while_grasping():
    response = NEEMData().get_source_container_while_pouring()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


# this method at the moment will return Null because of knowrob issue
@app.route("/knowrob/api/v1.0/get_source_container_pose_while_grasping")
def get_source_container_pose_while_grasping():
    response = NEEMData().get_source_container_pose_while_pouring()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_all_objects_with_roles_participates_in_actions")
def get_all_obj_participate_each_event():
    response = NEEMData().get_all_obj_roles_which_participate_each_event()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_shape_for_source_container_objects")
def get_shape_for_all_container_objects():
    response = NEEMData().get_shape_for_source_container_objects()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_color_for_source_container_object")
def get_color_for_all_container_objects():
    response = NEEMData().get_color_for_source_container_objects()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_target_obj_for_pouring")
def get_target_obj_for_pouring():
    response = NEEMData().get_target_obj_for_pouring()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_pouring_side")
def get_pouring_side_for_target_obj():
    response = NEEMData().get_pouring_side()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_max_pouring_angle_for_source_obj")
def get_max_pouring_angle_for_source_obj():
    response = NEEMData().get_max_pouring_angle_for_source_obj()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_min_pouring_angle_for_source_obj")
def get_min_pouring_angle_for_source_obj():
    response = NEEMData().get_min_pouring_angle_for_source_obj()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_pouring_event_time_duration")
def get_pouring_event_time_duration():
    response = NEEMData().get_pouring_event_time_duration()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_motion_for_pouring")
def get_motion_for_pouring():
    response = NEEMData().get_motion_for_pouring()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/get_hand_used_for_pouring")
def get_hand_used_for_pouring():
    response = NEEMData().get_hand_used_for_pouring()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


######################## VR NEEM logging ########################


@app.route("/knowrob/api/v1.0/create_actor", methods = ['GET'])
def create_actor():
    response = NEEMData().create_actor()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/create_actor_by_given_name", methods = ['GET', 'POST'])
def create_actor_by_given_name():
    actor_name = request.json['actor_name']
    print("actor with given name REST: ", actor_name)
    response = NEEMData().create_actor_by_given_name(actor_name)
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400

@app.route("/knowrob/api/v1.0/find_all_actors", methods = ['GET'])
def find_all_actors():
    response = NEEMData().find_all_actors()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400

@app.route("/knowrob/api/v1.0/get_time", methods = ['GET'])
def get_time():
    response = NEEMData().get_time()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


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

    # use the ast.literal_eval function to parse the string and create a dictionary object
    additional_information_dict_obj = []
    if(len(additional_information) != 0):
        additional_information_dict_obj = ast.literal_eval(additional_information)

    # print("create sub action call parent_action: %s , sub_action_type : %s , task_type: %s , start_time: %s , end_time: %s , objects_participated: %s , game_participant: %s "
    #       %(parent_action_iri, sub_action_type, task_type, start_time, end_time, objects_participated, game_participant))

    response = NEEMData().add_subaction_with_task(parent_action_iri, sub_action_type, task_type, start_time, end_time,
                                                  objects_participated, additional_information_dict_obj, game_participant)
    if response is not None:
        print("Sub task is added to the KB!", response)
        return jsonify(response), 200
    else:
        return jsonify(response), 400

@app.route("/knowrob/api/v1.0/add_additional_pouring_information", methods = ['GET', 'POST'])
def post_add_additional_pouring_information():
    parent_action_iri = request.json['parent_action_iri']
    sub_action_type = request.json['sub_action_type']
    max_pouring_angle = request.json['max_pouring_angle']
    min_pouring_angle = request.json['min_pouring_angle']
    source_container = request.json['source_container']
    destination_container = request.json['destination_container']
    pouring_pose = request.json['pouring_pose']

    # print("add additional info for pouring action with parent_action: %s , "
    #       "sub_action_type : %s , max_pouring_angle: %s , min_pouring_angle: %s , "
    #       "source_container: %s , destination_container: %s , pouring_pose: %s "
    #       %(parent_action_iri, sub_action_type, max_pouring_angle, min_pouring_angle, source_container,
    #         destination_container, pouring_pose))
    
    response = NEEMData().add_additional_pouring_information(parent_action_iri, sub_action_type, max_pouring_angle,
                                                             min_pouring_angle, source_container, destination_container,
                                                             pouring_pose)
    if response is not None:
        print("additional pouring information is added to the KB!", response)
        return jsonify(response), 200
    else:
        return jsonify(response), 400

@app.route("/knowrob/api/v1.0/create_episode", methods = ['GET', 'POST'])
def create_episode():
    game_participant = request.json['game_participant']
    print("create an episode with game_participant: %s "
          %(game_participant))
    NEEMData().create_actor_by_given_name(game_participant)

    response = NEEMData().create_episode(game_participant)
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/knowrob/api/v1.0/finish_episode", methods = ['GET', 'POST'])
def post_finish_episode():
    episode_iri = request.json['episode_iri']
    print("finish an episode with iri: %s " %(episode_iri))
    response = NEEMData().finish_episode(episode_iri)
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400

# @app.route("/knowrob/api/v1.0/hand_participate", methods = ['GET', 'POST'])
# def post_finish_episode():
#     hand_type = request.json['hand_type']
#     response = NEEMData().hand_participate_in_action(hand_type)
#     if response is not None:
#         return jsonify(response), 200
#     else:
#         return jsonify(response), 400