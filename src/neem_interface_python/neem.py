from typing import List

from neem_interface import NEEMInterface
from rosprolog_client import Prolog, atom


class NEEM:
    """
    Represents a NEEM and provides actions to access its properties
    """

    def __init__(self):
        self.neem_interface = NEEMInterface()
        self.prolog = Prolog()
        self.episode = self.prolog.ensure_once("kb_call(is_episode(Episode))")["Episode"]

    def get_transitions(self) -> List[str]:
        """
        Get a list of transition IRIs associated to this NEEM, sorted by time
        """
        top_level_action = self.get_top_level_action()
        res = self.prolog.ensure_once(f"""
            kb_call([
                holds({atom(top_level_action)}, dul:'hasTimeInterval', TimeInterval),
                holds(TimeInterval, soma:'hasIntervalBegin', StartTime),
                holds(TimeInterval, soma:'hasIntervalEnd', EndTime)
            ]).
        """)
        start_time = res["StartTime"]
        end_time = res["EndTime"]
        res = self.prolog.ensure_all_solutions(f"kb_call(is_transition(Transition)).")
        all_transitions = [sol["Transition"] for sol in res]
        transitions_by_time = dict()
        for transition in all_transitions:
            res = self.prolog.ensure_once(f"""
                kb_call([
                    holds({atom(transition)}, soma:'hasInitialScene', InitialScene),
                    is_state(InitialState), holds(InitialScene, dul:'includesEvent', InitialState),
                    has_time_interval(InitialState, TransitionStartTime, TransitionEndTime)
                 ]).
            """)
            transition_start_time = res["TransitionStartTime"]
            transition_end_time = res["TransitionEndTime"]
            if transition_start_time >= start_time and transition_end_time <= end_time:
                # This transition is part of this neem
                transitions_by_time[transition_start_time] = transition
        return [kv[1] for kv in sorted(transitions_by_time.items())]

    def get_top_level_action(self) -> str:
        solutions = self.prolog.ensure_all_solutions(f"""
            kb_call([
                is_action(Action), is_setting_for({atom(self.episode)}, Action)
            ]).
        """)
        return solutions[0]["Action"]

    def get_participants(self) -> List[str]:
        """
        Get a list of all things participating in any subaction of the episode.
        """
        top_level_action = self.get_top_level_action()
        solutions = self.prolog.ensure_all_solutions(f"""
            kb_call(has_participant({atom(top_level_action)}, Participant))
        """)
        participants = [solution["Participant"] for solution in solutions]
        subaction_solutions = self.prolog.ensure_all_solutions(f"""
            kb_call([
                is_action(Action), holds({atom(top_level_action)},dul:hasConstituent,Action),
                has_participant(Action, Participant)
            ]).
        """)
        subaction_participants = [solution["Participant"] for solution in subaction_solutions]
        return list(set(participants + subaction_participants))

    def get_trajectory(self, object_iri: str) -> List[dict]:
        """
        Get the trajectory of an object over the course of this NEEM.
        """
        top_level_action = self.get_top_level_action()
        res = self.prolog.ensure_once(f"kb_call(has_time_interval({atom(top_level_action)}, StartTime, EndTime))")
        start_time = res["StartTime"]
        end_time = res["EndTime"]
        return self.neem_interface.get_tf_trajectory(object_iri, start_time, end_time)

    @staticmethod
    def load(neem_dir: str):
        NEEMInterface().load_neem(neem_dir)
        return NEEM()
