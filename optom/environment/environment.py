from __future__ import print_function

class Environment(object):

    def __init__(self):
        self._vehicles = {}
        self._edges = {}

    @property
    def vehicles(self):
        return self._vehicles

    @property
    def vehicle(self, p_vid):
        return self._vehicles.get(p_vid)

    @property
    def edges(self):
        return self._edges

    def edge(self, p_edgid):
        return self._edges.get(p_edgid)

    def vehicles_on_edge(self, p_edgeid):
        return filter(lambda v: v.get("edgeid") == p_edgeid, self._vehicles.items())

    def add_vehicle(self, p_vehicle):
        self._vehicles[p_vehicle.getID()] = p_vehicle


class VehicleFactory(object):
    pass

