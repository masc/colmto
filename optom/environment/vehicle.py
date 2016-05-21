import random

class Vehicle(object):

    def __init__(self, p_vtype, p_speedsigma):
        self._vtype = p_vtype
        self._id = None
        self._starttime = None
        self._color = None
        self._maxspeed = int(round(random.gauss(p_vtype.get("maxSpeed"), p_speedsigma)))
        self._trajectory = {}

    @property
    def vtype(self):
        return self._vtype

    @property
    def id(self):
        return self._id

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, p_color):
        self._color = p_color

    @property
    def starttime(self):
        return self._starttime

    @property
    def maxspeed(self):
        return self._maxspeed

    @property
    def trajectory(self):
        return self._trajectory

    def provision(self, p_id, p_starttime):
        self._id = p_id if self._id is None else self._id
        self._starttime = p_starttime if self._starttime is None else self._starttime

    def __str__(self):
        return "{}({})".format(self._id, self._vtype.get("vClass"))

    def __repr__(self):
        return "{}({})".format(self._id, self._vtype.get("vClass"))
