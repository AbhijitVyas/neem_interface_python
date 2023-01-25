#!/usr/bin/env python3
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Optional
import time

from src.neem_interface_python.rosprolog_client import Prolog, atom

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
neem_uri = '/home/avyas/catkin_ws/src/pouring_apartment_neem/NEEM'

class NEEMData(object):
    """
    Low-level interface to KnowRob, which enables the easy access of NEEM data in Python.
    """

    def __init__(self):
        self.prolog = Prolog()
     
    # not working at the moment    
    #def clear_beliefstate(self):
    #    self.prolog.ensure_once(f"mem_clear_memory")

    # this method loads local neem to local kb(populates local mongodb)
    def load_neem_to_kb(self):
        # prolog exception will be raised if response is none
        response = self.prolog.ensure_once(f"remember({atom(neem_uri)})")
        return response

    def insert_fact_to_kb(self):
        # prolog exception will be raised if response is none
        response = self.prolog.ensure_once(f"remember({atom(neem_uri)})")
        return response

    def get_all_actions(self):
        # prolog exception will be raised if response is none
        response = self.prolog.ensure_once("findall([Act],is_action(Act), Act)")
        print(response)
        return response

    def get_all_actions_start_timestamps(self):
        # prolog exception will be raised if response is none
        response = self.prolog.ensure_once("findall([Begin, Evt], event_interval(Evt, Begin, _), StartTimes)")
        print(response)
        return response

    def get_all_actions_end_timestamps(self):
        # prolog exception will be raised if response is none
        response = self.prolog.ensure_once("findall([End, Evt], event_interval(Evt, _, End), EndTimes)")
        print(response)
        return response

    def get_all_objects_participates_in_actions(self):
        # prolog exception will be raised if response is none
        response = self.prolog.ensure_once("findall([Act, Obj], has_participant(Act, Obj), Obj)")
        return response

    def get_handpose_at_start_of_action(self):
        # prolog exception will be raised if response is none
        # TODO: This call has bug from knowrob side, fix it. Call Human hand once bug is fixed 
        response = self.prolog.once("executes_task(Action, Task),has_type(Task, soma:'Grasping'),event_interval(Action, Start, End),time_scope(Start, End, QScope),tf:tf_get_pose('http://knowrob.org/kb/pouring_hands_map.owl#right_hand_1', [map, Pose, Rotation], QScope,_)")
        print("response with poses: ", response)
        return response

    def get_source_container_while_grasping(self):
        # prolog exception will be raised if response is none
        response = self.prolog.ensure_once("has_type(Tsk, soma:'Grasping'),executes_task(Act, Tsk), has_participant(Act, Obj), has_type(Role, soma:'SourceContainer'), triple(Obj, dul:'hasRole', Role)")
        return response

    def get_source_container_pose_while_grasping(self):
        # prolog exception will be raised if response is none
        # TODO: This call has bug from knowrob side, fix it. Call Human hand once bug is fixed 
        response = self.prolog.once("has_type(Tsk, soma:'Grasping'),executes_task(Act, Tsk), has_participant(Act, Obj),event_interval(Act, Start, End),time_scope(Start, End, QScope),tf:tf_get_pose(Obj, [map, Pose, Rotation], QScope,_)")
        print("response with poses: ", response)
        return response

    def get_all_obj_roles_which_participate_each_event(self):
        # prolog exception will be raised if response is none
        # TODO: This call has bug from knowrob side, fix it. Call Human hand once bug is fixed 
        response = self.prolog.once("findall([Act, Obj, ObjType, Role], (has_participant(Act, Obj), has_type(Obj, ObjType), triple(Obj, dul:'hasRole', Role)) , Obj)")
        print("response with poses: ", response)
        return response
    
    def get_shape_for_source_container_objects(self):
        # prolog exception will be raised if response is none 
        response = self.prolog.once("has_type(Tsk, soma:'Grasping'),executes_task(Act, Tsk), has_participant(Act, Obj), "
                                    "has_type(Role, soma:'SourceContainer'),triple(Obj, dul:'hasRole', Role), triple(Obj, soma:'hasShape', Shape), has_region(Shape, ShapeRegion)")
        
        print("response with poses: ", response)
        return response


    def get_color_for_source_container_objects(self):
        # prolog exception will be raised if response is none 
        response = self.prolog.once("has_type(Tsk, soma:'Grasping'),executes_task(Act, Tsk), has_participant(Act, Obj), has_type(Role, soma:'SourceContainer'),"
                                    "triple(Obj, dul:'hasRole', Role), triple(Obj, soma:'hasColor', Color), has_region(Color, ColorRegion)")

        print("response with poses: ", response)
        return response


    def get_target_obj_for_pouring(self):
        # prolog exception will be raised if response is none 
        response = self.prolog.once("has_type(Tsk, 'http://www.ease-crc.org/ont/SOMA-ACT.owl#Pouring'),executes_task(Act, Tsk), has_participant(Act, Obj), has_type(Role, soma:'DestinationContainer'), triple(Obj, dul:'hasRole', Role)")
        print("response with poses: ", response)
        return response

    def get_pouring_side(self):
        # prolog exception will be raised if response is none 
        response = self.prolog.once("has_type(Tsk, 'http://www.ease-crc.org/ont/SOMA-ACT.owl#Pouring'),executes_task(Act, Tsk), has_participant(Act, Obj), "
                                    "triple(Obj, dul:'hasLocation', Location)")
        print("response with poses: ", response)
        return response

    def get_max_pouring_angle_for_source_obj(self):
        # prolog exception will be raised if response is none 
        response = self.prolog.once("triple(Individual, 'http://www.ease-crc.org/ont/SOMA-OBJ.owl#hasJointPositionMax', AngleValue)")
        print("response with poses: ", response)
        return response

    def get_min_pouring_angle_for_source_obj(self):
        # prolog exception will be raised if response is none 
        response = self.prolog.once("triple(Individual, 'http://www.ease-crc.org/ont/SOMA-OBJ.owl#hasJointPositionMin', AngleValue)")
        print("response with poses: ", response)
        return response
    
    def get_pouring_event_time_duration(self):
        # prolog exception will be raised if response is none 
        response = self.prolog.once("has_type(Tsk, 'http://www.ease-crc.org/ont/SOMA-ACT.owl#Pouring'),executes_task(Act, Tsk), event_interval(Act, Begin, End)")
        print("response with poses: ", response)
        return response
    
    def get_motion_for_pouring(self):
        # prolog exception will be raised if response is none 
        response = self.prolog.once("has_type(Tsk, 'http://www.ease-crc.org/ont/SOMA-ACT.owl#Pouring'),executes_task(Act, Tsk), "
                                    "triple(Motion, dul:'classifies', Act), triple(Motion,dul:'isClassifiedBy', Role), triple(Obj, dul:'hasRole', Role)")
        print("response with poses: ", response)
        return response
        
    def get_hand_used_for_pouring(self):
        # prolog exception will be raised if response is none 
        response = self.prolog.once("has_type(Tsk, 'http://www.ease-crc.org/ont/SOMA-ACT.owl#Pouring'),executes_task(Act, Tsk), has_type(Hand, soma:'Hand')")
        print("response with poses: ", response)
        return response
    
    # this method loads remote neem from neemhub to local kb(but do not populate local mongodb)
    #def load_remote_neem_to_kb(self, neem_id):
    #    self.prolog.ensure_once(f"knowrob_load_neem({atom(neem_id)})")
    