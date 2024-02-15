#!/usr/bin/env python3
import json
import sys
import os

from rosprolog_client import Prolog, atom
from utils.utils import Datapoint, Pose
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Optional
import time
import rospy

prolog = None
try:
    from rosprolog_client import Prolog
    prolog = Prolog()
except ImportError:
    rospy.logerr("No Knowrob services found")


from enum import Enum

class Actions(Enum):
    POURING_PARTICLES_WITH_TWO_CONTAINERS = ("pouring", "soma:'pouring'", "soma:'pour'", "No spil")
    POURING_PANCAKE = ("pouring", "soma:'pouring'", "soma:'pour'", "perfect shape")
    SPRINKLING_SALT = ("sprinkling", "soma:'sprinkling'", "soma:'sprinkle'", "on target")
    WATER_PLANT =     ("watering", "soma:'watering'", "soma:'pour'", "on target")
    # CUTTING_BREAD = ("cutting", )
    # CUTTING_FRUIT = ("cutting", )

    def __new__(cls, action_verb, soma_task_type, soma_action_type, goal_statement):
        obj = object.__new__(cls)
        obj.action_verb = action_verb
        obj.soma_task_type = soma_task_type
        obj.soma_action_type = soma_action_type
        return obj

class ActionCore:
    def __init__(self, action_verb: str = None, soma_task_type: str = None, soma_action_type: str = None,
                 source_obj: str = None,
                 soma_source_obj_role: str = None, target_obj: str = None, soma_target_obj_role: str = None,
                 substance: str = None,
                 soma_substance_role: str = None, amount: int = None, goal: str = None, unit: str = None):
        self.action_verb = action_verb
        self.soma_task_type = soma_task_type
        self.soma_action_type = soma_action_type
        self.source_obj = source_obj
        self.soma_source_obj_role = soma_source_obj_role
        self.target_obj = target_obj
        self.soma_target_obj_role = soma_target_obj_role
        self.substance = substance
        self.soma_substance_role = soma_substance_role
        self.amount = amount
        self.goal = goal
        self.unit = unit

    def print_values(self):
        print("Action verb: " + self.action_verb + " soma_task_type: " + self.soma_task_type +
              " soma_action_type: " + self.soma_action_type
              + " source_obj: " + self.source_obj + " soma_source_obj_role: " + self.soma_source_obj_role
              + "target_obj: " + self.target_obj + " soma_target_obj_role: " + self.soma_target_obj_role
              + "substance: " + self.substance + "amount: " + self.amount + "unit: " + self.unit
              + "goal: " + self.goal)


class BootstrapInterface:
    """
        Low-level interface to KnowRob, which enables the easy creation of NEEMs in Python.
        The class provides bootstrapping predicates that can be used to create a task learning experience
        between the teacher and a robot student
        """

    def __init__(self, task_instruction: str = None, action_core: ActionCore = None, task_iri: str = None,
                 action_iri: str = None, agent_iri: str = None, environment_iri: str = None):

        self.task_instruction = task_instruction
        self.action_core = action_core
        self.task_iri = task_iri
        self.action_iri = action_iri
        self.agent_iri = agent_iri
        self.agent_type = None
        self.environment_iri = environment_iri

    def define_task(self, task_instruction):
        """
        - add task definition to the Kb as fact and also process this NL instruction and save it as soma concepts such as Objs,
          Substances and action types etc.
        - First it adds the task instruction to the kb and crates an action core with related infromation from the NL,
          such as the source obj, destinaton obj, substance(optional), amount(optional) and, unit(optional)
        """
        # TODO use RASA library here to parse NL instruction
        # print("task_def: ", task_def)
        self.action_core = self.load_task_definition_to_nlp(task_instruction)
        self.action_core.print_values()
        task_def_query_response = prolog.ensure_once(f"""
                        kb_project([
                            has_type({atom(task_instruction)}, soma:'Natural_Language_Text')
                        ]).
                    """)
        return self.action_core

    def add_agent(self, agent):
        # somified agent value
        self.agent_iri = "soma:'" + agent + "'"
        self.agent_type = "dul:'Agent'"

    def load_task_to_kb(self):
        # add task, action and agent information to the kb
        task_type_query_response = self.add_task_type()

        self.task_iri = task_type_query_response['Task']
        self.action_iri = task_type_query_response['Action']

        print("Task iri", self.task_iri)
        print("Action iri", self.action_iri)

        # add source obj information to kb
        source_query_response = ""
        if self.action_core.source_obj != "":
            source_query_response = self.add_task_source_obj(task_type_query_response,
                                                             self.action_core.source_obj,
                                                             self.action_core.soma_source_obj_role)

        # add dest obj information to kb
        dest_query_response = ""
        if self.action_core.target_obj != "":
            dest_query_response = self.add_task_destination_obj(task_type_query_response,
                                                                self.action_core.target_obj,
                                                                self.action_core.soma_target_obj_role)

        # here only add substance if it is provided as
        substance_query_response = ""
        if self.action_core.substance != "":
            substance_query_response = self.add_task_substance(task_type_query_response,
                                                               self.action_core.substance,
                                                               self.action_core.soma_substance_role)


        goal_query_response = ""
        if self.action_core.goal != "":
            goal_query_response = self.add_task_goal(task_type_query_response,
                                                     self.action_core.goal)

        # print("task_type_query_response", task_type_query_response)
        # response include Instance of Task
        return (task_type_query_response, source_query_response, dest_query_response,
                substance_query_response, goal_query_response)

    def add_task_type(self):
        task_type_query_response = prolog.ensure_once(f"""
            kb_project([
                new_iri(Task, {atom(self.action_core.soma_task_type)}), 
                has_type(Task,{atom(self.action_core.soma_task_type)}),
                new_iri(Action, {atom(self.action_core.soma_action_type)}), 
                has_type(Action,dul:'Action'), 
                executes_task({atom(self.action_core.soma_action_type)},Task),
                holds(Action, dul:'hasParticipant', {atom(self.agent_iri)}), 
                has_type({atom(self.agent_iri)}, {atom(self.agent_type)})
            ]).
        """)
        return task_type_query_response

    def add_environment(self, environment: str):
        self.environment_iri = "soma:'" + environment + "'"
        environment_type = "dul:'PhysicalPlace'"
        source_query_response = prolog.ensure_once(f"""
            kb_project([
            holds({atom(self.action_iri)}, dul: 'hasParticipant', {atom(self.environment_iri)}), 
            has_type({atom(self.environment_iri)}, {atom(environment_type)}).
        """)

    def add_task_source_obj(self, task_type_query_response, src_obj, src_obj_role):
        source_query_response = prolog.ensure_once(f"""
            kb_project([
                holds({atom(task_type_query_response['Action'])}, dul:'hasParticipant', {atom(src_obj)}), 
                new_iri(SourceRole, {atom(src_obj_role)}),
                has_type(SourceRole, {atom(src_obj_role)}), 
                has_role({atom(src_obj)}, SourceRole)
            ]).
        """)
        return source_query_response

    def add_task_destination_obj(self, task_type_query_response, dest_obj, dest_obj_role):
        dest_query_response = prolog.ensure_once(f"""
            kb_project([
                holds({atom(task_type_query_response['Action'])}, dul:'hasParticipant', {atom(dest_obj)}), 
                new_iri(DestRole, {atom(dest_obj_role)}),
                has_type(DestRole, {atom(dest_obj_role)}), 
                has_role({atom(dest_obj)}, DestRole)
            ]).
        """)
        return dest_query_response

    def add_task_substance(self, task_type_query_response, substance, substance_role):
        substance_query_response = prolog.ensure_once(f"""
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
        task_goal_query_response = prolog.ensure_once(f"""
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

    # TODO: Ask/Check for start and stop conditions for pouring task with Daniel or Mihai
    # Here, initial condition is that the substance is inside of source container and destination container is empty
    # Here, final condition is that the substance is inside of destination container and source container is empty
    # TODO: Lock obj relationships for the pre condition only, hence use during or similar predicate to indicate this.
    def add_pouring_particles_task_start_stop_conditions(self, action_iri):
        conditional_query_response = prolog.ensure_once(f"""
            kb_project([
                new_iri(PreState, soma:'State'), has_type(PreState, soma:'State'),
                holds(PreState, dul:'hasParticipant', {atom(self.action_core.substance)}),
                holds(PreState, dul:'hasParticipant', {atom(self.action_core.source_obj)}),
                holds({atom(action_iri)}, dul:'hasPrecondition', PreState),
                holds({atom(self.action_core.source_obj)}, soma:'contains', {atom(self.action_core.substance)} ),
                holds({atom(action_iri)}, soma:'during', PreState),
                
                new_iri(PostState, soma:'State'), has_type(PostState, soma:'State'),
                holds(PostState, dul:'hasParticipant', {atom(self.action_core.substance)}),
                holds(PostState, dul:'hasParticipant', {atom(self.action_core.target_obj)}),
                holds({atom(action_iri)}, dul:'hasPostcondition', PostState),
                holds({atom(self.action_core.target_obj)} , soma:'contains', {atom(self.action_core.substance)}),
                holds({atom(action_iri)}, soma:'during', PostState)
            ]).
        """)

        return conditional_query_response

    # def add_pouring_pancake_task_start_stop_conditions(self, action_iri):
    #     conditional_query_response = prolog.ensure_once(f"""
    #         kb_project([
    #             new_iri(PreScene, soma:'Scene'), has_type(PreScene, soma:'Scene'),
    #             new_iri(PreState, soma:'State'), has_type(PreState, soma:'State'),
    #             holds(PreScene dul:'includesEvent', PreState),
    #             holds({atom(action_iri)}, dul:'hasPrecondition', PreScene),
    #             holds({atom(self.action_core.substance)}, soma:'isInsideOf', {atom(self.action_core.source_obj)}),
    #
    #             new_iri(PostScene, soma:'Scene'), has_type(PostScene, soma:'Scene'),
    #             new_iri(PostState, soma:'State'), has_type(PostState, soma:'State'),
    #             holds(PostScene dul:'includesEvent', PostState),
    #             holds({atom(action_iri)}, dul:'hasPrecondition', PostScene),
    #             holds({atom(self.action_core.substance)}, soma:'isOntopOf', {atom(self.action_core.target_obj)})
    #         ]).
    #     """)
    #
    #     return conditional_query_response

    # TODO: Ask/Check for start and stop conditions for pouring task with Daniel or Mihai
    # Here, initial condition is that the substance is inside of source container and destination container is empty
    # Here, final condition is that the substance is inside of destination container and source container is empty
    # TODO: Lock obj relationships for the pre condition only, hence use during or similar predicate to indicate this.
    def add_pouring_particles_task_goal_conditions(self, action_iri):
        goal_conditional_query_response = prolog.ensure_once(f"""
            kb_project([
                new_iri(Goal, dul:'Goal'), has_type(Goal, dul:'Goal'),
                holds({atom(action_iri)}, soma:'hasGoal', Goal),
                holds(Goal, dul:'hasPart', {atom(self.action_core.substance)}),
                holds(Goal, dul:'hasPart', {atom(self.action_core.target_obj)}),
                holds({atom(self.action_core.target_obj)} , soma:'contains', {atom(self.action_core.substance)}),
                holds({atom(action_iri)}, soma:'during', Goal)
            ]).
        """)

        return goal_conditional_query_response

    def add_primitive_action_to_task(self, action_iri, primitive_actions):

        # somified agent and environment values
        task_primitive_query_response = ""

        task_type = ""
        action_type = ""
        obj_participated = ""
        for index, primitive_action in enumerate(primitive_actions):
            if primitive_action == 'pickup':
                task_type = "soma:'PickingUp'"
                action_type = "soma:'PickUp'"
                obj_participated = self.action_core.source_obj
            elif primitive_action == 'align':
                task_type = "soma:'Aligning'"
                action_type = "soma:'Align'"
                obj_participated = self.action_core.source_obj
            elif primitive_action == 'tilt':
                task_type = "soma:'Tilting'"
                action_type = "soma:'Tilt'"
                obj_participated = self.action_core.source_obj
            elif primitive_action == 'putdown':
                task_type = "soma:'PuttingDown'"
                action_type = "soma:'PutDown'"
                obj_participated = self.action_core.source_obj

            if index < (len(primitive_actions) - 1):
                # add post condition as long as next primitive_action exists in the list
                # TODO: add pre and post conditions as primitive actions here such that it can create a link between them
                # TODO: use action_iri as well
                task_primitive_query_response = prolog.ensure_once(f"""
                    kb_project([
                        new_iri(Task, {atom(task_type)}), has_type(Task,{atom(task_type)}), 
                        new_iri(Action, {atom(action_type)}), has_type(Action,dul:'Action'), 
                        executes_task({atom(action_type)},Task),
                        holds(Action, dul:'hasParticipant', {atom(self.agent_iri)}), 
                        has_type({atom(self.agent_iri)}, {atom(self.agent_type)}),
                        holds(Action, dul:'hasParticipant', {atom(obj_participated)})
                    ]).
                """)
            else:
                # Add without post condition
                # TODO: add pre and post conditions as primitive actions here such that it can create a link between them
                # TODO: use action_iri as well
                task_primitive_query_response = prolog.ensure_once(f"""
                    kb_project([
                        new_iri(Task, {atom(task_type)}), has_type(Task,{atom(task_type)}), 
                        new_iri(Action, {atom(action_type)}), has_type(Action,dul:'Action'), 
                        executes_task({atom(action_type)},Task),
                        holds(Action, dul:'hasParticipant', {atom(self.agent_iri)}), 
                        has_type({atom(self.agent_iri)}, {atom(self.agent_type)}),
                        holds(Action, dul:'hasParticipant', {atom(obj_participated)})
                    ]).
                """)
        return task_primitive_query_response


    def get_type(self, obj):
        response = prolog.ensure_once(f"""
                        kb_project([
                            findall([Type],(has_type({atom(obj)}, Type)), Type)
                        ]).
                    """)
        return response

    def get_role(self, obj):
        response = prolog.ensure_once(f"""
                        kb_project([
                            findall([Role],(has_role({atom(obj)}, Role)), Role)
                        ]).
                    """)
        return response

    def load_task_definition_to_nlp(self, task_def: str):
        action_core: ActionCore = ActionCore()
        # json_str = {}
        if task_def.__contains__("pour") or task_def.__contains__("Pour"):

            action_core.action_verb = "pouring"
            action_core.substance = "Water"
            action_core.source_obj = "Cup"
            action_core.target_obj = "Bowl"
            action_core.goal = "No Spilling"
            action_core.amount = ""
            action_core.unit = ""
            # json_str = '{"action_verb": "pouring", "substance": "Water", ' '"source_object": "", "target_object": "Bowl",' '"unit": "ml", "goal": "pour without spilling", "motion_verb": "tilting", "amount": "50"}'

        elif task_def.__contains__("cut") or task_def.__contains__("Cut"):
            action_core.action_verb = "cutting"
            action_core.substance = ""
            action_core.source_obj = "Knife"
            action_core.target_obj = "Bread"
            action_core.goal = "Cut Slices"
            action_core.amount = "3"
            action_core.unit = ""
            # json_str = '{"action_verb": "cutting", "substance": "", ' '"source_object": "Knife", "target_object": "Bread",' '"unit": "slice", "goal": "cut without damage", "motion_verb": "slicing", "amount": "5"}'

        # get somified values for rasa output
        action_core = self.get_somified_values_for_rasa_output(action_core)
        # data = json.loads(json_str)
        return action_core

    def get_somified_values_for_rasa_output(self, action_core: ActionCore):
        if action_core.action_verb.__contains__("pour"):
            action_core.soma_task_type = "soma:'Pouring'"
            action_core.soma_action_type = "soma:'Pour'"

            # these roles are common for all pouring examples, e.g. pancake or particles
            if action_core.source_obj != "":
                action_core.soma_source_obj_role = "soma:'Item'"
                action_core.source_obj = "soma:'" + action_core.source_obj + "'"

            if action_core.target_obj != "":
                action_core.soma_target_obj_role = "soma:'Item'"
                action_core.target_obj = "soma:'" + action_core.target_obj + "'"

            if action_core.substance != "":
                action_core.soma_substance_role = "soma:'PouredObject'"
                action_core.substance = "soma:'" + action_core.substance + "'"

        elif action_core.action_verb.__contains__("cut"):
            action_core.soma_task_type = "soma:'Cutting'"
            action_core.soma_action_type = "soma:'Cut'"
            if action_core.source_obj != "":
                action_core.soma_source_obj_role = "soma:'Cutter'"
                action_core.source_obj = "soma:'" + action_core.source_obj + "'"

            if action_core.target_obj != "":
                action_core.soma_target_obj_role = "soma:'CutObject'"
                action_core.target_obj = "soma:'" + action_core.target_obj + "'"

        elif action_core.action_verb.__contains__("clean"):
            action_core.soma_task_type = "soma:'Cleaning'"
            action_core.soma_action_type = "soma:'Clean'"

            if action_core.source_obj != "":
                action_core.soma_source_obj_role = "soma:'Cleaner'"  # todo: add role cleaner to soma, e.g. sponge is a cleaner
                action_core.source_obj = "soma:'" + action_core.source_obj + "'"

            if action_core.target_obj != "":
                action_core.soma_target_obj_role = "soma:'DirtyObject'"  # todo: add DirtyObject as some role, e.g. surface is a dirty surface
                action_core.target_obj = "soma:'" + action_core.target_obj + "'"

            if action_core.substance != "":
                action_core.soma_substance_role = "soma:'CleaningSubstance'"  # todo: add CleaningSubstance as some role, e.g. water is a CleaningSubstance
                action_core.substance = "soma:'" + action_core.substance + "'"

        return action_core
