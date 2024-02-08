#!/usr/bin/env python3
import json
import sys
import os

from rosprolog_client import Prolog, atom
from utils.utils import Datapoint, Pose
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Optional
import time

from tqdm import tqdm

class ActionCore:
    def __init__(self, action_verb: str, source_obj: str, target_obj: str, substance: str, amount: int, goal: str, unit: str):
        self.action_verb = action_verb
        self.source_obj = source_obj
        self.target_obj = target_obj
        self.substance = substance
        self.amount = amount
        self.goal = goal
        self.unit = unit

class BootstrapInterface:
    """
        Low-level interface to KnowRob, which enables the easy creation of NEEMs in Python.
        It provides bootstrapping predicates that can be used to create a task learning experience between teacher and a robot student
        """

    def __init__(self, task_instruction: str, action_core: ActionCore, task_iri: str, action_iri: str, agent_iri: str, environment_iri: str):
        self.prolog = Prolog()
        self.pool_executor = ThreadPoolExecutor(max_workers=4)


    def define_task(self, task_def, environment, agent):
        """
        - add task definition to the Kb as fact and also process this NL instruction and save it as soma concepts such as Objs, Substances and action types etc.

        """
        # TODO use RASA library here to parse NL instruction
        # print("task_def: ", task_def)
        data = self.load_task_definition_to_nlp(task_def)
        # print("data: ", data)
        task_type = ""
        if data["action_verb"].__contains__("pour"):
            task_type = "soma:'Pouring'"
            action_type = "soma:'Pour'"
            if data["source_object"] != "":
                src_obj_role = "soma:'SourceContainer'"
                src_obj = "soma:'" + data["source_object"] + "'"

            if data["target_object"] != "":
                dest_obj_role = "soma:'DestinationContainer'"
                dest_obj = "soma:'" + data["target_object"] + "'"

            if data["substance"] != "":
                substance_role = "soma:'PouredObject'"
                substance = "soma:'" + data["substance"] + "'"

        elif data["action_verb"].__contains__("cut"):
            task_type = "soma:'Cutting'"
            action_type = "soma:'Cut'"
        elif data["action_verb"].__contains__("clean"):
            task_type = "soma:'Cleaning'"
            action_type = "soma:'Clean'"
        elif data["action_verb"].__contains__("shake"):
            task_type = "soma:'Shaking'"
            action_type = "soma:'Shake'"
        elif data["action_verb"].__contains__("open"):
            task_type = "soma:'Opening'"
            action_type = "soma:'Open'"

        # somified agent and environment values
        environment = "soma:'" + environment + "'"
        environment_type = "dul:'PhysicalPlace'"
        agent = "soma:'" + agent + "'"
        agent_type = "dul:'Agent'"

        task_def_query_response = self.prolog.ensure_once(f"""
                        kb_project([
                            has_type({atom(task_def)}, soma:'Natural_Language_Text')
                        ]).
                    """)
        if task_type != "":
            task_type_query_response = self.add_task_type(task_type, action_type, environment, environment_type,
                                                          agent,
                                                          agent_type)
            source_query_response = ""
            if data["source_object"] != "":
                source_query_response = self.add_task_source_obj(task_type_query_response, src_obj, src_obj_role)

            dest_query_response = ""
            if data["target_object"] != "":
                dest_query_response = self.add_task_destination_obj(task_type_query_response, dest_obj,
                                                                    dest_obj_role)

            # here only add substance if it is provided as
            substance_query_response = ""
            if data["substance"] != "":
                substance_query_response = self.add_task_substance(task_type_query_response, substance,
                                                                   substance_role)

            goal_query_response = ""
            if data["goal"] != "":
                goal_query_response = self.add_task_goal(task_type_query_response, data["goal"])

            # print("task_type_query_response", task_type_query_response)
            # response include Instance of Task
            return task_type_query_response, source_query_response, dest_query_response, substance_query_response, goal_query_response

        return

    def add_task_type(self, task_type, action_type, environment, environment_type, agent, agent_type):
        task_type_query_response = self.prolog.ensure_once(f"""
            kb_project([
                new_iri(Task, {atom(task_type)}), has_type(Task,{atom(task_type)}), 
                new_iri(Action, {atom(action_type)}), has_type(Action,dul:'Action'), 
                executes_task({atom(action_type)},Task),
                holds(Action, dul:'hasParticipant', {atom(environment)}), has_type({atom(environment)}, {atom(environment_type)}),
                holds(Action, dul:'hasParticipant', {atom(agent)}), has_type({atom(agent)}, {atom(agent_type)})
            ]).
        """)
        return task_type_query_response

    def add_task_source_obj(self, task_type_query_response, src_obj, src_obj_role):
        source_query_response = self.prolog.ensure_once(f"""
            kb_project([
                holds({atom(task_type_query_response['Action'])}, dul:'hasParticipant', {atom(src_obj)}), 
                new_iri(SourceRole, {atom(src_obj_role)}),
                has_type(SourceRole, {atom(src_obj_role)}), 
                has_role({atom(src_obj)}, SourceRole)
            ]).
        """)
        return source_query_response

    def add_task_destination_obj(self, task_type_query_response, dest_obj, dest_obj_role):
        dest_query_response = self.prolog.ensure_once(f"""
            kb_project([
                holds({atom(task_type_query_response['Action'])}, dul:'hasParticipant', {atom(dest_obj)}), 
                new_iri(DestRole, {atom(dest_obj_role)}),
                has_type(DestRole, {atom(dest_obj_role)}), 
                has_role({atom(dest_obj)}, DestRole)
            ]).
        """)
        return dest_query_response

    def add_task_substance(self, task_type_query_response, substance, substance_role):
        substance_query_response = self.prolog.ensure_once(f"""
                    kb_project([
                        holds({atom(task_type_query_response['Action'])}, dul:'hasParticipant', {atom(substance)}),
                        new_iri(SubRole, {atom(substance_role)}),
                        has_type(SubRole, {atom(substance_role)}), 
                        has_role({atom(substance)}, SubRole)
                    ]).
                """)
        return substance_query_response

    # TODO: Add conditional statement such as for no spilling to occur,
    #  all particles must be inside destinationObj, this can be done by adding a state with objs as participants.
    # TODO: Ask Mihai how to use Goal with state with conditions
    def add_task_goal(self, task_type_query_response, task_goal):
        task_goal_query_response = self.prolog.ensure_once(f"""
            kb_project([
                new_iri(TaskGoal, dul:'Goal'), has_type(TaskGoal, dul:'Goal'),
                holds({atom(task_type_query_response['Task'])}, soma:'hasGoal', TaskGoal),
                new_iri(TaskGoalText, soma:'Natural_Language_Text'),
                has_type(TaskGoalText, soma:'Natural_Language_Text'),
                holds(TaskGoal, dul:'hasDataValue', {atom(task_goal)}),
                holds(TaskGoal, dul:'isExpressedBy', TaskGoalText)
            ]).
        """)
        return task_goal_query_response

    # TODO: Ask Mihai how to use StateTransition here with initial conditions
    def add_task_start_condition(self, action_iri, start_condition):
        task_type_query_response = self.prolog.ensure_once(f"""
            kb_project([
                new_iri(PreScene, soma:'Scene'), has_type(PreScene, soma:'Scene'),
                new_iri(PreState, soma:'State'), has_type(PreState, soma:'State'),
                holds(PreScene dul:'includesEvent', PreState), 
                holds({atom(action_iri)}, dul:'hasPrecondition', PreScene)
            ]).
        """)

    def add_primitive_action_to_task(self, action_iri, primitive_actions, environment, agent):

        # somified agent and environment values
        task_primitive_query_response = ""
        environment = "soma:'" + environment + "'"
        environment_type = "dul:'PhysicalPlace'"
        agent = "soma:'" + agent + "'"
        agent_type = "dul:'Agent'"

        task_type = ""
        action_type = ""
        for index, primitive_action in enumerate(primitive_actions):
            if primitive_action == 'pickup':
                task_type = "soma:'PickingUp'"
                action_type = "soma:'PickUp'"
            elif primitive_action == 'align':
                task_type = "soma:'Aligning'"
                action_type = "soma:'Align'"
            elif primitive_action == 'tilt':
                task_type = "soma:'Tilting'"
                action_type = "soma:'Tilt'"
            elif primitive_action == 'putdown':
                task_type = "soma:'PuttingDown'"
                action_type = "soma:'PutDown'"

            if index < (len(primitive_actions) - 1):
                # add post condition as long as next primitive_action exists in the list
                # TODO: add pre and post conditions as primitive actions here such that it can create a link between them
                # TODO: use action_iri as well
                task_primitive_query_response = self.prolog.ensure_once(f"""
                    kb_project([
                        new_iri(Task, {atom(task_type)}), has_type(Task,{atom(task_type)}), 
                        new_iri(Action, {atom(action_type)}), has_type(Action,dul:'Action'), 
                        executes_task({atom(action_type)},Task),
                        holds(Action, dul:'hasParticipant', {atom(environment)}), has_type({atom(environment)}, {atom(environment_type)}),
                        holds(Action, dul:'hasParticipant', {atom(agent)}), has_type({atom(agent)}, {atom(agent_type)})
                    ]).
                """)
            else:
                # Add without post condition
                # TODO: add pre and post conditions as primitive actions here such that it can create a link between them
                # TODO: use action_iri as well
                task_primitive_query_response = self.prolog.ensure_once(f"""
                    kb_project([
                        new_iri(Task, {atom(task_type)}), has_type(Task,{atom(task_type)}), 
                        new_iri(Action, {atom(action_type)}), has_type(Action,dul:'Action'), 
                        executes_task({atom(action_type)},Task),
                        holds(Action, dul:'hasParticipant', {atom(environment)}), has_type({atom(environment)}, {atom(environment_type)}),
                        holds(Action, dul:'hasParticipant', {atom(agent)}), has_type({atom(agent)}, {atom(agent_type)})
                    ]).
                """)
        return task_primitive_query_response

        # def somified_task_action(self, action, src_obj, dest_obj):
        #     if action == 'pickup':
        #         task_type = "soma:'PickingUp'"
        #         action_type = "soma:'PickUp'"
        #         src_obj_role = "soma:'PickUpObj'"
        #         src_obj = "soma:'" + src_obj + "'"
        #         dest_obj_role = ""
        #         dest_obj = ""
        #     elif action == 'align':
        #         task_type = "soma:'Aligning'"
        #         action_type = "soma:'Align'"
        #     elif action == 'tilt':
        #         task_type = "soma:'Tilting'"
        #         action_type = "soma:'Tilt'"
        #     elif action == 'putdown':
        #         task_type = "soma:'PuttingDown'"
        #         action_type = "soma:'PutDown'"
        #     elif action.__contains__("pour"):
        #         task_type = "soma:'Pouring'"
        #         action_type = "soma:'Pour'"
        #         src_obj_role = "soma:'SourceContainer'"
        #         src_obj = "soma:'" + src_obj + "'"
        #         dest_obj_role = "soma:'DestinationContainer'"
        #         dest_obj = "soma:'" + dest_obj + "'"
        #
        #
        #     elif action.__contains__("cut"):
        #         task_type = "soma:'Cutting'"
        #         action_type = "soma:'Cut'"
        #         src_obj_role = "soma:'Cutter'"
        #         src_obj = "soma:'" + src_obj + "'"
        #         dest_obj_role = "soma:'Cuttie'"
        #         dest_obj = "soma:'" + dest_obj + "'"
        #     elif action.__contains__("clean"):
        #         task_type = "soma:'Cleaning'"
        #         action_type = "soma:'Clean'"
        #         src_obj_role = "soma:'Cleaner'"
        #         src_obj = "soma:'" + src_obj + "'"
        #         dest_obj_role = "soma:'DirtySurface'"
        #         dest_obj = "soma:'" + dest_obj + "'"
        #     elif action.__contains__("shake"):
        #         task_type = "soma:'Shaking'"
        #         action_type = "soma:'Shake'"
        #         src_obj_role = "soma:'SourceContainer'"
        #         src_obj = "soma:'" + src_obj + "'"
        #         dest_obj_role = "soma:'DestinationLocation'"
        #         dest_obj = "soma:'" + dest_obj + "'"
        #
        #     return task_type, action_type, src_obj, src_obj_role, dest_obj, dest_obj_role

    def get_type(self, obj):
        response = self.prolog.ensure_once(f"""
                        kb_project([
                            findall([Type],(has_type({atom(obj)}, Type)), Type)
                        ]).
                    """)
        return response

    def get_role(self, obj):
        response = self.prolog.ensure_once(f"""
                        kb_project([
                            findall([Role],(has_role({atom(obj)}, Role)), Role)
                        ]).
                    """)
        return response

    def load_task_definition_to_nlp(self, task_def: str):
        json_str = {}
        if task_def.__contains__("pour") or task_def.__contains__("Pour"):
            json_str = '{"action_verb": "pouring", "substance": "Water", ' '"source_object": "", "target_object": "Bowl",' '"unit": "ml", "goal": "pour without spilling", "motion_verb": "tilting", "amount": "50"}'

        elif task_def.__contains__("cut") or task_def.__contains__("Cut"):
            json_str = '{"action_verb": "cutting", "substance": "", ' '"source_object": "Knife", "target_object": "Bread",' '"unit": "slice", "goal": "cut without damage", "motion_verb": "slicing", "amount": "5"}'

        data = json.loads(json_str)
        return data
