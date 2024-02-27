#!/usr/bin/env python3

from neem_interface_python.rosprolog_client import Prolog, atom
from neem_interface_python.neem_interface import NEEMInterface

neem_uri = '/home/avyas/catkin_ws/src/pouring_apartment_neem/NEEM'

class NEEMData(object):
    """
    Low-level interface to KnowRob, which enables the easy access of NEEM data in Python.
    """

    def __init__(self):
        self.prolog = Prolog()
        self.neem_interface = NEEMInterface()

    def load_neem_to_kb(self): 
        return self.prolog.ensure_once(f"remember({atom(neem_uri)})") 

    def insert_fact_to_kb(self):
        return self.prolog.ensure_once(f"remember({atom(neem_uri)})")

    def get_all_actions(self):
        return self.prolog.ensure_once("findall([Act],is_action(Act), Act)")

    def get_all_actions_start_timestamps(self):
        return self.prolog.ensure_once("findall([Begin, Evt], event_interval(Evt, Begin, _), StartTimes)")

    def get_all_actions_end_timestamps(self):
        return self.prolog.ensure_once("findall([End, Evt], event_interval(Evt, _, End), EndTimes)")

    def get_all_objects_participates_in_actions(self):
        return self.prolog.ensure_once("findall([Act, Obj], has_participant(Act, Obj), Obj)")

    def get_handpose_at_start_of_action(self):
        return self.prolog.once("executes_task(Action, Task),has_type(Task, soma:'Grasping'),event_interval(Action, Start, End),time_scope(Start, End, QScope),tf:tf_get_pose('http://knowrob.org/kb/pouring_hands_map.owl#right_hand_1', [map, Pose, Rotation], QScope,_)")

    def get_source_container_while_pouring(self):
        return self.prolog.ensure_once("has_type(Tsk, soma:'Pouring'),executes_task(Act, Tsk), has_participant(Act, Obj), has_type(Role, soma:'SourceContainer'), has_role(Obj, Role), has_type(Obj, ObjType)")


    def get_source_container_pose_while_pouring(self):
        return self.prolog.once("has_type(Tsk, soma:'Pouring'),executes_task(Act, Tsk), has_participant(Act, Obj), has_type(Role, soma:'SourceContainer'), has_role(Obj, Role), holds(Role, dul:'isObservableAt', TI), holds(Obj, dul:'hasRegion', ThreeDPose), holds(ThreeDPose, dul:'isObservableAt', TI), holds(ThreeDPose, soma:'hasPositionData', Pose)")

    def get_target_container_pose_while_pouring(self):
        return self.prolog.once("has_type(Tsk, soma:'Pouring'),executes_task(Act, Tsk), has_participant(Act, Obj), has_type(Role, soma:'DestinationContainer'), has_role(Obj, Role), holds(Role, dul:'isObservableAt', TI), holds(Obj, dul:'hasRegion', ThreeDPose), holds(ThreeDPose, dul:'isObservableAt', TI), holds(ThreeDPose, soma:'hasPositionData', Pose)")

    def get_all_obj_roles_which_participate_each_event(self):
        return self.prolog.once("findall([Act, Obj, ObjType, Role], (has_participant(Act, Obj), has_type(Obj, ObjType), triple(Obj, dul:'hasRole', Role)) , Obj)")
    
    def get_shape_for_source_container_objects(self):
        return self.prolog.once("has_type(Tsk, soma:'Grasping'),executes_task(Act, Tsk), has_participant(Act, Obj), "
                                    "has_type(Role, soma:'SourceContainer'),triple(Obj, dul:'hasRole', Role), triple(Obj, soma:'hasShape', Shape), has_region(Shape, ShapeRegion)")

    def get_color_for_source_container_objects(self):
        return self.prolog.once("has_type(Tsk, soma:'Grasping'),executes_task(Act, Tsk), has_participant(Act, Obj), has_type(Role, soma:'SourceContainer'),"
                                    "triple(Obj, dul:'hasRole', Role), triple(Obj, soma:'hasColor', Color), has_region(Color, ColorRegion)")

    def get_target_obj_for_pouring(self):
        return self.prolog.once("has_type(Tsk, soma:'Pouring'),executes_task(Act, Tsk), has_participant(Act, Obj), has_type(Role, soma:'DestinationContainer'), has_role(Obj, Role), has_type(Obj, ObjType)")

    def get_pouring_side(self):
        return self.prolog.once("has_type(Tsk, 'http://www.ease-crc.org/ont/SOMA-ACT.owl#Pouring'),executes_task(Act, Tsk), has_participant(Act, Obj), "
                                    "triple(Obj, dul:'hasLocation', Location)")

    def get_max_pouring_angle_for_source_obj(self):
        return self.prolog.once("has_type(Tsk, soma:'Pouring'),executes_task(Act, Tsk), has_participant(Act, Obj), has_type(Role, soma:'SourceContainer'), has_role(Obj, Role), holds(Role, dul:'isObservableAt', TI), holds(Obj, dul:'hasRegion', SixDPoseMaxAngle), holds(SixDPoseMaxAngle, dul:'isObservableAt', TI), holds(SixDPoseMaxAngle, soma:'hasMaxPouringAngleData', MAXAngle)")

    def get_min_pouring_angle_for_source_obj(self):
        return self.prolog.once("has_type(Tsk, soma:'Pouring'),executes_task(Act, Tsk), has_participant(Act, Obj), has_type(Role, soma:'SourceContainer'), has_role(Obj, Role), holds(Role, dul:'isObservableAt', TI), holds(Obj, dul:'hasRegion', SixDPoseMaxAngle), holds(SixDPoseMaxAngle, dul:'isObservableAt', TI), holds(SixDPoseMaxAngle, soma:'hasMinPouringAngleData', MinAngle)")
    
    def get_pouring_event_time_duration(self):
       return self.prolog.once("has_type(Tsk, soma:'Pouring'),executes_task(Act, Tsk), event_interval(Act, Begin, End)")
    
    def get_motion_for_pouring(self):
        return self.prolog.once("has_type(Tsk, 'http://www.ease-crc.org/ont/SOMA-ACT.owl#Pouring'),executes_task(Act, Tsk), "
                                    "triple(Motion, dul:'classifies', Act), triple(Motion,dul:'isClassifiedBy', Role), triple(Obj, dul:'hasRole', Role)")
        
    def get_hand_used_for_pouring(self):
        return self.prolog.once("has_type(Tsk, 'http://www.ease-crc.org/ont/SOMA-ACT.owl#Pouring'),executes_task(Act, Tsk), has_type(Hand, soma:'Hand')")

    def add_subaction_with_task(self, parent_action_iri,
                                sub_action_type, task_type,
                                start_time, end_time, objects_participated, additional_information, game_participant):
        return self.neem_interface.add_vr_subaction_with_task(parent_action_iri, sub_action_type, task_type,
                                                                  start_time, end_time, objects_participated,
                                                                  additional_information, game_participant)

    def add_additional_pouring_information(self, parent_action_iri, sub_action_type, max_pouring_angle,
                                           min_pouring_angle, source_container, destination_container, pouring_pose):
        return self.neem_interface.add_additional_pouring_information(parent_action_iri, sub_action_type,
                                                                          max_pouring_angle, min_pouring_angle,
                                                                          source_container, destination_container,
                                                                          pouring_pose)

    def create_actor(self):
        return self.neem_interface.create_actor()

    def find_all_actors(self):
        response = self.neem_interface.find_all_actors()
        response_data = []
        for actor in response.get('Actor'):
            data = {}
            data['Actor'] = actor[0]
            response_data.append(data)
        return response_data

    def create_actor_by_given_name(self, actor_name):
        return self.neem_interface.create_actor_by_given_name(actor_name)

    def create_episode(self, game_participant):
        return self.neem_interface.start_vr_episode(game_participant)

    def finish_episode(self, episode_iri):
        return self.neem_interface.stop_vr_episode(episode_iri)

    def get_time(self):
        return self.neem_interface.get_time()