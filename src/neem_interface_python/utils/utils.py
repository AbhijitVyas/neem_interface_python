#!/usr/bin/env python3
import sys
import os
sys.path.append(os.getcwd() + "/../../../src/")

from rosprolog_client import atom, Prolog
from typing import List

from scipy.spatial.transform import Rotation
import dateutil.parser



class Pose:
    def __init__(self, reference_frame: str, pos: List[float], ori: Rotation):
        self.reference_frame = reference_frame
        self.pos = pos
        self.ori = ori

    @staticmethod
    def from_prolog(prolog_pose: List):
        return Pose(reference_frame=prolog_pose[0], pos=prolog_pose[1], ori=Rotation.from_quat(prolog_pose[2]))

    def to_knowrob_string(self) -> str:
        """
        Convert to a KnowRob pose "[reference_cs, [x,y,z],[qx,qy,qz,qw]]"
        """
        quat = self.ori.as_quat()   # qxyzw
        return f"[{atom(self.reference_frame)}, [{self.pos[0]},{self.pos[1]},{self.pos[2]}], [{quat[0]}," \
               f"{quat[1]},{quat[2]},{quat[3]}]]"


class Datapoint:
    def __init__(self, timestamp: float, frame: str, reference_frame: str, pos: List[float], ori: Rotation,
                 wrench: List[float] = None):
        """
        :param timestamp:
        :param reference_frame: e.g. 'world'
        :param pos: [x,y,z] in m
        :param ori: [qx,qy,qz,qw] in a right-handed coordinate system
        :param wrench: [fx,fy,fz,mx,my,mz] in N / Nm
        """
        self.timestamp = timestamp
        self.frame = frame
        self.reference_frame = reference_frame
        self.pos = pos
        self.ori = ori
        self.wrench = wrench

    @staticmethod
    def from_prolog(prolog_dp: dict, frame=""):
        ori = Rotation.from_quat(prolog_dp["term"][2][2])
        return Datapoint(timestamp=prolog_dp["term"][1], frame=frame, reference_frame=prolog_dp["term"][2][0],
                              pos=prolog_dp["term"][2][1], ori=ori)

    def to_knowrob_string(self) -> str:
        """
        Convert to a KnowRob pose "[reference_cs, [x,y,z],[qx,qy,qz,qw]]"
        """
        quat = self.ori.as_quat()   # qxyzw
        return f"[{atom(self.reference_frame)}, [{self.pos[0]},{self.pos[1]},{self.pos[2]}], [{quat[0]}," \
               f"{quat[1]},{quat[2]},{quat[3]}]]"

    @staticmethod
    def from_tf(tf_msg: dict):
        timestamp = dateutil.parser.parse(tf_msg["header"]["stamp"]["$date"]).timestamp()
        frame = tf_msg["child_frame_id"]
        reference_frame = tf_msg["header"]["frame_id"]
        trans = tf_msg["transform"]["translation"]
        pos = [trans["x"], trans["y"], trans["z"]]
        rot = tf_msg["transform"]["rotation"]
        ori = Rotation.from_quat([rot["x"], rot["y"], rot["z"], rot["w"]])
        return Datapoint(timestamp, frame, reference_frame, pos, ori)

    @staticmethod
    def from_unreal(timestamp: float, frame: str, reference_frame: str, pos_cm: List[float], ori_lhs: List[float]):
        """
        See https://github.com/robcog-iai/UUtils/blob/master/Source/UConversions/Public/Conversions.h#L59-L74
        :param timestamp: In seconds
        :param frame:
        :param reference_frame:
        :param pos_cm: [x,y,z] in cm
        :param ori_lhs: [qx,qy,qz,qw] in a left-handed coordinate system
        :return:
        """
        # Convert cm to mm
        pos_m = [p / 100.0 for p in pos_cm]
        pos_rhs = [pos_m[1], pos_m[0], pos_m[2]]

        # Convert handedness of coordinate systems
        x, y, z, w = ori_lhs
        ori_rhs = Rotation.from_quat([-x, y, -z, w])
        return Datapoint(timestamp, frame, reference_frame, pos_rhs, ori_rhs)


def expand_rdf_namespace(prolog: Prolog, short_namespace: str) -> str:
    return prolog.ensure_once(f"rdf_prefixes:rdf_current_prefix({atom(short_namespace)}, URI)")["URI"]


def compact_rdf_namespace(prolog: Prolog, long_namespace: str) -> str:
    return prolog.ensure_once(f"rdf_prefixes:rdf_current_prefix(NS, {atom(long_namespace)})")["NS"]
