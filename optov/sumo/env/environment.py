from __future__ import print_function

class Environment(object):

    def __init__(self):
        self._vehicles = {}
        self._edges = {}

    def getVehicles(self):
        return self._vehicles

    def getVehicle(self, p_vid):
        return self._vehicles.get(p_vid)

    def getEdges(self):
        return self._edges

    def getEdge(self, p_edgid):
        return self._edges.get(p_edgid)

    def getVehiclesOnEdge(self, p_edgeid):
        return filter(lambda v: v.get("edgeid") == p_edgeid, self._vehicles.items())

    def addVehicle(self, p_vehicle):
        self._vehicles[p_vehicle.getID()] = p_vehicle