#!/usr/bin/env python3
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Optional
import time

from src.neem_interface_python.rosprolog_client import Prolog, atom

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
neem_uri = '/home/avyas/catkin_ws/src/pouring_hands_neem/NEEM-1'

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

    # this method loads remote neem from neemhub to local kb(but do not populate local mongodb)
    #def load_remote_neem_to_kb(self, neem_id):
    #    self.prolog.ensure_once(f"knowrob_load_neem({atom(neem_id)})")
 