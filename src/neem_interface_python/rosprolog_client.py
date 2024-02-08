"""
Rosprolog client loosely coupled to ROS and compatible with Python 3
"""
#!/usr/bin/env python3
import sys
import os
sys.path.append(os.getcwd() + "/../../../src/")

from utils.rosbridge import ros_client
import json
from enum import Enum
from typing import Optional, Dict, List, Iterator
from urllib.parse import urlparse
import re

import roslibpy



class PrologException(Exception):
    pass


class PrologNextSolutionResponse(Enum):
    NO_SOLUTION = 0
    WRONG_ID = 1
    QUERY_FAILED = 2
    OK = 3


class Upper(object):
    def __init__(self, iterable):
        self._iter = iter(iterable)

    def __next__(self):  # Py3-style iterator interface
        return next(self._iter)  # builtin next() function calls

    def __iter__(self):
        return self


class PrologQuery(object):
    def __init__(self, query_str: str, simple_query_srv: roslibpy.Service, next_solution_srv: roslibpy.Service,
                 finish_srv: roslibpy.Service, iterative=True):
        """
        This class wraps around the different rosprolog services to provide a convenient python interface.
        :param iterative: if False, all solutions will be calculated by rosprolog during the first service call
        """
        self._simple_query_srv = simple_query_srv
        self._next_solution_srv = next_solution_srv
        self._finish_query_srv = finish_srv

        self._finished = False
        self._query_id = None
        result = self._simple_query_srv.call(roslibpy.ServiceRequest({"id": self.get_id(), "query": query_str,
                                                                      "mode": 1 if iterative else 0}))
        if not result["ok"]:
            raise PrologException('Prolog query failed: {}'.format(result["message"]))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()

    def solutions(self) -> Iterator[Dict]:
        try:
            while not self._finished:
                next_solution = self._next_solution_srv.call(roslibpy.ServiceRequest({"id": self.get_id()}))
                if next_solution[
                    "status"] == PrologNextSolutionResponse.OK.value:  # Have to compare to .value here because roslibpy msg does not have types
                    yield self._json_to_dict(next_solution["solution"])
                elif next_solution["status"] == PrologNextSolutionResponse.WRONG_ID.value:
                    raise PrologException(
                        f'Query id {self.get_id()} invalid. Maybe another process terminated our query?')
                elif next_solution["status"] == PrologNextSolutionResponse.QUERY_FAILED.value:
                    raise PrologException(f'Prolog query failed: {next_solution["solution"]}')
                elif next_solution["status"] == PrologNextSolutionResponse.NO_SOLUTION.value:
                    break
                else:
                    raise PrologException(f'Unknown query status {next_solution["solution"]}')
        finally:
            self.finish()

    def finish(self):
        if not self._finished:
            try:
                self._finish_query_srv.call(roslibpy.ServiceRequest({"id": self.get_id()}))
            finally:
                self._finished = True

    def get_id(self):
        """
        :rtype: str
        """
        if self._query_id is None:
            self._query_id = 'PYTHON_QUERY_{}'.format(roslibpy.Time.now().to_nsec())
        return self._query_id

    def _json_to_dict(self, json_text):
        """
        :type json_text: str
        :rtype: dict
        """
        return json.loads(json_text)


class Prolog(object):
    def __init__(self, name_space='rosprolog'):
        """
        :type name_space: str
        :param timeout: Amount of time in seconds spend waiting for rosprolog to become available.
        :type timeout: int
        """
        ros_hostname = urlparse(os.environ["ROS_MASTER_URI"]).hostname
        self._simple_query_srv = roslibpy.Service(ros_client, f'{name_space}/query', "json_prolog_msgs/srv/PrologQuery")
        self._next_solution_srv = roslibpy.Service(ros_client, f'{name_space}/next_solution',
                                                   "json_prolog_msgs/srv/PrologNextSolution")
        self._finish_query_srv = roslibpy.Service(ros_client, f'{name_space}/finish',
                                                  "json_prolog_msgs/srv/PrologFinish")

    def query(self, query_str):
        """
        Returns an Object which asks rosprolog for one solution at a time.
        :type query_str: str
        :rtype: PrologQuery
        """
        return PrologQuery(query_str, simple_query_srv=self._simple_query_srv,
                           next_solution_srv=self._next_solution_srv, finish_srv=self._finish_query_srv)

    def once(self, query_str: str) -> Optional[Dict]:
        """
        Call rosprolog once and immediately finish the query.
        Return None if Prolog returned false.
        Return a Dict mapping all variables in the query to atoms if the query succeeded.
        Throw an exception if query execution failed (syntax errors, connection errors etc.)
        """
        q = None
        try:
            q = PrologQuery(query_str, simple_query_srv=self._simple_query_srv,
                            next_solution_srv=self._next_solution_srv, finish_srv=self._finish_query_srv)
            return next(Upper(q.solutions()))
        except StopIteration:
            return None
        finally:
            if q is not None:
                q.finish()

    def ensure_once(self, query_str) -> Dict:
        """
        Same as once, but throws an exception if Prolog returns false.
        """
        res = self.once(query_str)
        if res is None:
            raise PrologException(f"Prolog returned false.\nQuery: {query_str}")
        return res

    def all_solutions(self, query_str: str) -> List[Dict]:
        """
        Requests all solutions from rosprolog, this might take a long time
        Return an empty List if Prolog returned False.
        Return a List of Dicts mapping all variables in the query to atoms if the query succeeded.
        Throw an exception if query execution failed (syntax errors, connection errors etc.)
        """
        return list(PrologQuery(query_str,
                                iterative=False,
                                simple_query_srv=self._simple_query_srv,
                                next_solution_srv=self._next_solution_srv,
                                finish_srv=self._finish_query_srv).solutions())

    def ensure_all_solutions(self, query_str) -> List[Dict]:
        """
        Same as all_solutions, but raise an exception if Prolog returns false.
        """
        res = self.all_solutions(query_str)
        if len(res) == 0:
            raise PrologException(f"Prolog returned false.\nQuery: {query_str}")
        return res


def atom(string: str):
    try:
        if re.match(".+:'.+'", string):
            # Has namespace prefix --> don't wrap in quotes
            return string
        return f"'{string}'"
    except:
        print(string)
        raise RuntimeError()
