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
# @app.route("/clear_kb")
# def clear_knowledge_base():
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

@app.route("/get_all_actions_end_time")
def get_all_actions_end_time_stamps():
    response = NEEMData().get_all_actions_end_timestamps()
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


# this method will not return any pose since knowrob tf_get_pose has some bug and does not return any value at the 
#  moment 
@app.route("/get_handpose_at_start_of_action")
def get_handpose_at_start_of_action():
    response = NEEMData().get_handpose_at_start_of_action()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_source_container_while_grasping")
def get_source_container_while_grasping():
    response = NEEMData().get_source_container_while_grasping()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


# this method at the moment will return Null because of knowrob issue
@app.route("/get_source_container_pose_while_grasping")
def get_source_container_pose_while_grasping():
    response = NEEMData().get_source_container_pose_while_grasping()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_all_objects_with_roles_participates_in_actions")
def get_all_obj_participate_each_event():
    response = NEEMData().get_all_obj_roles_which_participate_each_event()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_shape_for_source_container_objects")
def get_shape_for_all_container_objects():
    response = NEEMData().get_shape_for_source_container_objects()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_color_for_source_container_object")
def get_color_for_all_container_objects():
    response = NEEMData().get_color_for_source_container_objects()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_target_obj_for_pouring")
def get_target_obj_for_pouring():
    response = NEEMData().get_target_obj_for_pouring()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_pouring_side")
def get_pouring_side_for_target_obj():
    response = NEEMData().get_pouring_side()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_max_pouring_angle_for_source_obj")
def get_max_pouring_angle_for_source_obj():
    response = NEEMData().get_max_pouring_angle_for_source_obj()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_min_pouring_angle_for_source_obj")
def get_min_pouring_angle_for_source_obj():
    response = NEEMData().get_min_pouring_angle_for_source_obj()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_pouring_event_time_duration")
def get_pouring_event_time_duration():
    response = NEEMData().get_pouring_event_time_duration()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_motion_for_pouring")
def get_motion_for_pouring():
    response = NEEMData().get_motion_for_pouring()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@app.route("/get_hand_used_for_pouring")
def get_hand_used_for_pouring():
    response = NEEMData().get_hand_used_for_pouring()
    if response is not None:
        return jsonify(response), 200
    else:
        return jsonify(response), 400
    