import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Optional
import time

from tqdm import tqdm

from src.neem_interface_python.rosprolog_client import Prolog, atom
from src.neem_interface_python.utils.utils import Datapoint, Pose

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class NEEMError(Exception):
    pass


class NEEMInterface:
    """
    Low-level interface to KnowRob, which enables the easy creation of NEEMs in Python.
    For more ease of use, consider using the Episode object in a 'with' statement instead (see below).
    """

    def __init__(self):
        self.prolog = Prolog()
        self.pool_executor = ThreadPoolExecutor(max_workers=4)

        # Load neem-interface.pl into KnowRob
        neem_interface_path = "/home/avyas/catkin_ws/src/neem_interface_python/src/neem-interface/neem-interface/neem-interface.pl"
        print("neem interface path", neem_interface_path)
        self.prolog.ensure_once("ensure_loaded('" + neem_interface_path + "')")

    def __del__(self):
        # Wait for all currently running futures
        self.pool_executor.shutdown(wait=True)

    def clear_beliefstate(self):
        self.prolog.ensure_once("mem_clear_memory")

    ### NEEM Creation ###############################################################

    def start_episode(self, task_type: str, env_owl: str, env_owl_ind_name: str, env_urdf: str,
                      agent_owl: str, agent_owl_ind_name: str, agent_urdf: str, start_time: float = None):
        """
        Start an episode and return the prolog atom for the corresponding action.
        """
        q = f"mem_episode_start(Action, {atom(task_type)}, {atom(env_owl)}, {atom(env_owl_ind_name)}, {atom(env_urdf)}," \
            f"{atom(agent_owl)}, {atom(agent_owl_ind_name)}, {atom(agent_urdf)}," \
            f"{start_time if start_time is not None else time.time()})"
        res = self.prolog.ensure_once(q)
        return res["Action"]

    def stop_episode(self, neem_path: str, end_time: float = None):
        """
        End the current episode and save the NEEM to the given path
        """
        return self.prolog.ensure_once(
            f"mem_episode_stop({atom(neem_path)}, {end_time if end_time is not None else time.time()})")

    def add_subaction_with_task(self, parent_action, sub_action_type="dul:'Action'", task_type="dul:'Task'",
                                start_time: float = None, end_time: float = None) -> str:
        """
        Assert a subaction of a given type, and an associated task of a given type.
        """
        q = f"mem_add_subaction_with_task({atom(parent_action)},{atom(sub_action_type)},{atom(task_type)},SubAction)"
        solution = self.prolog.ensure_once(q)
        action_iri = solution["SubAction"]
        if start_time is not None and end_time is not None:
            self.prolog.ensure_once(f"kb_project(has_time_interval({atom(action_iri)}, {start_time}, {end_time}))")
        return action_iri

    def add_participant_with_role(self, action: str, participant: str, role_type="dul:'Role'") -> None:
        """
        Assert that something was a participant with a given role in an action.
        Participant must already have been inserted into the knowledge base.
        """
        q = f"mem_add_participant_with_role({atom(action)}, {atom(participant)}, {atom(role_type)})"
        self.prolog.ensure_once(q)

    def assert_tf_trajectory(self, points: List[Datapoint]):
        print(f"Inserting {len(points)} points")
        for point in tqdm(points):
            ee_pose_str = point.to_knowrob_string()
            self.prolog.ensure_once(f"""
                time_scope({point.timestamp}, {point.timestamp}, QS),
                tf_set_pose({atom(point.frame)}, {ee_pose_str}, QS).
            """)

    def assert_transition(self, agent_iri: str, object_iri: str, start_time: float, end_time: float) -> Tuple[
        str, str, str]:
        res = self.prolog.ensure_once(f"""
            kb_project([
                new_iri(InitialScene, soma:'Scene'), is_individual(InitialScene), instance_of(InitialScene, soma:'Scene'),
                new_iri(InitialState, soma:'State'), is_state(InitialState),
                has_participant(InitialState, {atom(object_iri)}),
                has_participant(InitialState, {atom(agent_iri)}),
                holds(InitialScene, dul:'includesEvent', InitialState),
                has_time_interval(InitialState, {start_time}, {start_time}),

                new_iri(TerminalScene, soma:'Scene'), is_individual(TerminalScene), instance_of(TerminalScene, soma:'Scene'),
                new_iri(TerminalState, soma:'State'), is_state(TerminalState),
                has_participant(TerminalState, {atom(object_iri)}),
                has_participant(TerminalState, {atom(agent_iri)}),
                holds(TerminalScene, dul:'includesEvent', TerminalState),
                has_time_interval(TerminalState, {end_time}, {end_time}),

                new_iri(Transition, dul:'Transition'), is_individual(Transition), instance_of(Transition, soma:'StateTransition'),
                holds(Transition, soma:'hasInitialScene', InitialScene),
                holds(Transition, soma:'hasTerminalScene', TerminalScene)
            ]).
        """)
        transition_iri = res["Transition"]
        initial_state_iri = res["InitialState"]
        terminal_state_iri = res["TerminalState"]
        return transition_iri, initial_state_iri, terminal_state_iri

    def assert_agent_with_effector(self, effector_iri: str, agent_type="dul:'PhysicalAgent'",
                                   agent_iri: str = None) -> str:
        if agent_iri is None:
            agent_iri = self.prolog.ensure_once(f"""
                kb_project([
                    new_iri(Agent, dul:'Agent'), is_individual(Agent), instance_of(Agent, {atom(agent_type)})
                ]).""")["Agent"]
        self.prolog.ensure_once(f"kb_project(has_end_link({atom(agent_iri)}, {atom(effector_iri)}))")
        return agent_iri

    def assert_state(self, participant_iris: List[str], start_time: float = None, end_time: float = None,
                     state_class="soma:'State'", state_type="soma:'StateType'") -> str:
        state_iri = self.prolog.ensure_once(f"""
            kb_project([
                new_iri(State, soma:'State'), is_individual(State), instance_of(State, {atom(state_class)}),
                new_iri(StateType, soma:'StateType'), is_individual(StateType), instance_of(StateType, {atom(state_type)}), 
                holds(StateType, dul:'classifies',  State)
            ])
        """)["State"]
        if start_time is not None and end_time is not None:
            self.prolog.ensure_once(f"kb_project(has_time_interval({atom(state_iri)}, {start_time}, {end_time}))")
        for iri in participant_iris:
            self.prolog.ensure_once(f"kb_project(has_participant({atom(state_iri)}, {atom(iri)}))")
        return state_iri

    def assert_situation(self, agent_iri: str, involved_objects: List[str], situation_type="dul:'Situation'") -> str:
        situation_iri = self.prolog.ensure_once(f"""
            kb_project([
                new_iri(Situation, {atom(situation_type)}), is_individual(Situation), instance_of(Situation, {atom(situation_type)}),
                holds(Situation, dul:'includesAgent', {atom(agent_iri)})
            ])
        """)["Situation"]
        for obj_iri in involved_objects:
            self.prolog.ensure_once(f"kb_project(holds({atom(situation_iri)}, dul:'includesObject', {atom(obj_iri)}))")
        return situation_iri

    def assert_object_pose(self, obj_iri: str, obj_pose: Pose, start_time: float = None, end_time: float = None):
        print(f"Object pose of {obj_iri} at {start_time}: {obj_pose.to_knowrob_string()}")
        if start_time is not None and end_time is not None:
            qs_query = f"time_scope({start_time}, {end_time}, QS)"
        elif start_time is not None and end_time is None:
            qs_query = f"time_scope({start_time}, {time.time()}, QS)"
        else:
            qs_query = f"time_scope({time.time()}, {time.time()}, QS)"
        self.prolog.ensure_once(
            f"tf_logger_enable, {qs_query}, tf_set_pose({atom(obj_iri)}, {obj_pose.to_knowrob_string()}, QS),"
            f"tf_logger_disable")

    def assert_object_trajectory(self, obj_iri: str, obj_poses: List[Pose], start_times: List[float],
                                 end_times: List[float], insert_last_pose_synchronously=True):
        """
        :param insert_last_pose_synchronously: Ensure that the last pose of the trajectory has been inserted when this
        method returns
        """
        # Insert in reversed order, so it becomes easy to wait for the last pose of the trajectory
        obj_poses_reversed = list(reversed(obj_poses))
        start_times_reversed = list(reversed(start_times))
        end_times_reversed = list(reversed(end_times))
        obj_iris = [obj_iri] * len(obj_poses_reversed)
        generator = self.pool_executor.map(self.assert_object_pose, obj_iris, obj_poses_reversed, start_times_reversed,
                                           end_times_reversed)
        if insert_last_pose_synchronously:
            next(generator)

    ### NEEM Parsing ###############################################################

    def load_neem(self, neem_path: str):
        """
        Load a NEEM into the KnowRob knowledge base.
        """
        self.prolog.ensure_once(f"mem_clear_memory, remember({atom(neem_path)})")

    def get_all_actions(self, action_type: str = None) -> List[str]:
        if action_type is not None:  # Filter by action type
            query = f"is_action(Action), instance_of(Action, {atom(action_type)})"
        else:
            query = "is_action(Action)"
        res = self.prolog.ensure_all_solutions(query)
        if len(res) > 0:
            return list(set([dic["Action"] for dic in
                             res]))  # Deduplicate: is_action(A) may yield the same action more than once
        else:
            raise NEEMError("Failed to find any actions")

    def get_all_states(self) -> List[str]:
        res = self.prolog.ensure_all_solutions("is_state(State)")
        if len(res) > 0:
            return list(set([dic["State"] for dic in res]))  # Deduplicate
        else:
            raise NEEMError("Failed to find any states")

    def get_interval_for_event(self, event: str) -> Optional[Tuple[float, float]]:
        res = self.prolog.ensure_once(f"event_interval({atom(event)}, Begin, End)")
        if res is None:
            return res
        return res["Begin"], res["End"]

    def get_object_pose(self, obj: str, timestamp: float = None) -> Pose:
        if timestamp is None:
            query = f"mem_tf_get({atom(obj)}, Pose)"
        else:
            query = f"mem_tf_get({atom(obj)}, Pose, {timestamp})"
        return Pose.from_prolog(self.prolog.ensure_once(query)["Pose"])

    def get_tf_trajectory(self, obj: str, start_timestamp: float, end_timestamp: float) -> List:
        res = self.prolog.ensure_once(f"tf_mng_trajectory({atom(obj)}, {start_timestamp}, {end_timestamp}, Trajectory)")
        return res["Trajectory"]

    def get_wrench_trajectory(self, obj: str, start_timestamp: float, end_timestamp: float) -> List:
        res = self.prolog.ensure_once(
            f"wrench_mng_trajectory({atom(obj)}, {start_timestamp}, {end_timestamp}, Trajectory)")
        return res["Trajectory"]

    def get_tasks_for_action(self, action: str) -> List[str]:
        res = self.prolog.ensure_all_solutions(f"""kb_call([executes_task({atom(action)}, Task), 
                                                           instance_of(Task, TaskType), 
                                                           subclass_of(TaskType, dul:'Task')])""")
        return [dic["Task"] for dic in res]

    def get_triple_objects(self, subject: str, predicate: str) -> List[str]:
        """
        Catch-all function for getting the 'object' values for a subject-predicate-object triple.
        :param subject: IRI of the 'subject' of the triple
        :param predicate: IRI of the 'predicate' of the triple
        """
        res = self.prolog.ensure_all_solutions(f"""kb_call(holds({atom(subject)}, {atom(predicate)}, X))""")
        if len(res) > 0:
            return list(set([dic["X"] for dic in res]))  # Deduplicate
        else:
            raise NEEMError("Failed to find any objects for triple")

    def get_triple_subjects(self, predicate: str, object: str) -> List[str]:
        """
        Catch-all function for getting the 'subject' values for a subject-predicate-object triple.
        :param predicate: IRI of the 'predicate' of the triple
        :param object: IRI of the 'object' of the triple
        """
        res = self.prolog.ensure_all_solutions(f"""kb_call(holds(X, {atom(predicate)}, {atom(object)}))""")
        if len(res) > 0:
            return list(set([dic["X"] for dic in res]))  # Deduplicate
        else:
            raise NEEMError("Failed to find any subjects for triple")

    ################ VR experiment related calls #################

    def create_actor(self):
        # create an actor
        naturalPersonQueryResponse = self.prolog.ensure_once(f"""
                kb_project([
                    new_iri(Actor, dul:'NaturalPerson'), has_type(Actor, dul:'NaturalPerson')
                ]).
            """)
        print("new Actor iri", naturalPersonQueryResponse["Actor"])
        return naturalPersonQueryResponse

    def find_all_actors(self):
        response = self.prolog.ensure_once("findall([Actor],(is_agent(Actor), has_type(Actor, dul:'NaturalPerson')), Actor)")
        return response

    def create_actor_by_given_name(self, actor_name):
        response = self.prolog.ensure_once(f"""
                kb_project([
                    has_type({atom(actor_name)}, dul:'NaturalPerson')
                ]).
            """)
        return response
    
    def get_time(self):
        response = self.prolog.ensure_once("get_time(Time)")
        print("response with time: ", response)
        return response

    
    # TODO use episode iri so that you do not need to remember the action, but if it does not work then it is fine.
    def add_vr_subaction_with_task(self, parent_action_iri, sub_action_type,
                                   task_type,
                                   start_time, end_time,
                                   objects_participated,
                                   game_participant) -> str:
        # get an actor if it exists otherwise create a new one
        
        
        self.create_actor_by_given_name(game_participant)
        
        actionQueryResponse = self.prolog.ensure_once(f"""
                kb_project([
                    new_iri(SubAction, {atom(sub_action_type)}), has_type(SubAction, {atom(sub_action_type)}),
                    holds({atom(sub_action_type)}, rdfs:subClassOf, dul:'Action'),
                    new_iri(Task, {atom(task_type)}), has_type(Task,{atom(task_type)}), executes_task(SubAction,Task),
                    holds({atom(task_type)}, rdfs:subClassOf, dul:'PhysicalTask'),
                    triple({atom(parent_action_iri)}, dul:hasConstituent, SubAction),
                    new_iri(TimeInterval, dul:'TimeInterval'),
                    has_type(TimeInterval,dul:'TimeInterval'),
                    holds(SubAction, dul:'hasTimeInterval', TimeInterval),
                    holds(TimeInterval, soma:'hasIntervalBegin', {float(start_time)}),
                    holds(TimeInterval, soma:'hasIntervalEnd', {float(end_time)}),
                    has_type({atom(game_participant)}, dul:'NaturalPerson'), is_performed_by(SubAction,{atom(game_participant)})
                ]).
            """)
        # for each object do this for the action with iri
        
        # print("objects_participated from rest call", objects_participated)
        objects_participated = objects_participated.replace("[", "")
        objects_participated = objects_participated.replace("]", "")
        objects = objects_participated.split(",")
        # print("objects split: ", objects)
        for obj in objects:
            objParticipateQueryResponse = self.prolog.ensure_once(f"""
                kb_project([
                    holds({atom(actionQueryResponse['SubAction'])}, dul:'hasParticipant', {atom(obj)})
                ]).
            """)
        
        # kb_project([holds('http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Action_DFTQXKCS', 
        # dul:'hasParticipant', 'http://knowrob.org/kb/iai-apartment.owl#right_hand_1')])

        return actionQueryResponse


    def start_vr_episode(self, game_participant, game_start_time):
        """
        - Start an episode and return the prolog atom for the corresponding response.
        - Here you get time later once the tf logger has started logging the tf frames so that you can assign 
        it(as start time) to the top level action and extra tf frames can be ignored
        """
        # get an actor if it exists otherwise create a new one
        self.create_actor_by_given_name(game_participant)
        episodeQueryResponse = self.prolog.ensure_once(f"""
                tf_logger_enable,
                kb_project([
                    new_iri(Episode, soma:'Episode'), has_type(Episode, soma:'Episode'),
                    new_iri(Action, dul:'Action'), has_type(Action, dul:'Action'),
                    new_iri(TimeInterval, dul:'TimeInterval'),
                    has_type(TimeInterval,dul:'TimeInterval'),
                    holds(Action, dul:'hasTimeInterval', TimeInterval),
                    holds(TimeInterval, soma:'hasIntervalBegin', {float(game_start_time)}),
                    new_iri(Task, dul:'Task'), has_type(Task,dul:'Task'), executes_task(Action,Task),
                    is_setting_for(Episode,Task),
                    triple(Episode, dul:includesAction, Action),
                    has_type({atom(game_participant)}, dul:'NaturalPerson'), is_performed_by(Action,{atom(game_participant)}),
                    triple(Episode, dul:includesAgent, {atom(game_participant)}),
                    new_iri(Role, soma:'AgentRole'), has_type(Role, soma:'AgentRole'), has_role({atom(game_participant)},Role)
                ]).
            """)
        return episodeQueryResponse

    def stop_vr_episode(self, episode_iri, game_end_time):
        """
        - stop an episode and return the prolog atom for the corresponding action.
        - Here you get time first so that you can assign it to the top level action(as end time)
        and then stop the tf logger so extra frames can be ignored
        """
        episodeQueryResponse = self.prolog.ensure_once(f"""
                tf_logger_disable,
                triple({atom(episode_iri)}, dul:'includesAction', Action),
                holds(Action, dul:'hasTimeInterval', TimeInterval),
                kb_project([
                     holds(TimeInterval, soma:'hasIntervalEnd', {float(game_end_time)})
                ]).
            """)
        return episodeQueryResponse

    # def hand_participate_in_action(self, hand_type):
        
    
class Episode:
    """
    Convenience object and context manager for NEEM creation. Can be used in a 'with' statement to automatically
    start and end a NEEM context (episode).
    """

    def __init__(self, neem_interface: NEEMInterface, task_type: str, env_owl: str, env_owl_ind_name: str,
                 env_urdf: str, agent_owl: str, agent_owl_ind_name: str, agent_urdf: str, neem_output_path: str,
                 start_time=None):
        self.neem_interface = neem_interface
        self.task_type = task_type
        self.env_owl = env_owl
        self.env_owl_ind_name = env_owl_ind_name
        self.env_urdf = env_urdf
        self.agent_owl = agent_owl
        self.agent_owl_ind_name = agent_owl_ind_name
        self.agent_urdf = agent_urdf
        self.neem_output_path = neem_output_path

        self.top_level_action_iri = None
        self.episode_iri = None
        self.start_time = start_time if start_time is not None else time.time()

    def __enter__(self):
        self.top_level_action_iri = self.neem_interface.start_episode(self.task_type, self.env_owl,
                                                                      self.env_owl_ind_name, self.env_urdf,
                                                                      self.agent_owl,
                                                                      self.agent_owl_ind_name, self.agent_urdf,
                                                                      self.start_time)
        self.episode_iri = \
            self.neem_interface.prolog.ensure_once(
                f"kb_call(is_setting_for(Episode, {atom(self.top_level_action_iri)}))")[
                "Episode"]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.neem_interface.stop_episode(self.neem_output_path)
