# -*- coding: utf-8 -*-
# @package optom
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of Overtaking Manoeuvres project.   #
# # Copyright (c) 2016, Malte Aschermann (malte.aschermann@tu-clausthal.de)   #
# # This program is free software: you can redistribute it and/or modify      #
# # it under the terms of the GNU Lesser General Public License as            #
# # published by the Free Software Foundation, either version 3 of the        #
# # License, or (at your option) any later version.                           #
# #                                                                           #
# # This program is distributed in the hope that it will be useful,           #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# # GNU Lesser General Public License for more details.                       #
# #                                                                           #
# # You should have received a copy of the GNU Lesser General Public License  #
# # along with this program. If not, see http://www.gnu.org/licenses/         #
# #############################################################################
# @endcond
from __future__ import print_function
from optom.common.enum import Enum
import vehicle

CELL_TYPE = Enum(["FREE", "BLOCKED", "VEHICLE"])


class Cell(object):

    def __init__(self, p_state=CELL_TYPE.FREE, p_vehicle=None):
        self._state = p_state
        self._vehicle = p_vehicle

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, p_state):
        self._state = CELL_TYPE.VEHICLE
        return self

    @property
    def vehicle(self):
        return self._vehicle

    @vehicle.setter
    def vehicle(self, p_vehicle):
        if self._state == CELL_TYPE.FREE:
            self._state = CELL_TYPE.VEHICLE
            self._vehicle = p_vehicle
        else:
            print("Crash into ", __name__, self._state)
        return self


class Environment(object):

    def __init__(self):
        self._grid = [[Cell(), Cell(CELL_TYPE.BLOCKED)] for _ in xrange(10)] \
                     + [[Cell(), Cell()] for _ in xrange(10)] \
                     + [[Cell(), Cell(CELL_TYPE.BLOCKED)] for _ in xrange(10)]

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

    @property
    def grid(self):
        return self._grid

    def add_vehicle(self, p_vehicle_id, p_position):
        if self.free(p_position) and p_vehicle_id not in self.vehicles:
            self.vehicles[p_vehicle_id] = vehicle.Vehicle(id=p_vehicle_id,
                                                          environment=self,
                                                          position=p_position
                                                          )
        return self

    def vehicles_on_edge(self, p_edgeid):
        return filter(
            lambda v: v.get("edgeid") == p_edgeid,
            self._vehicles.items()
        )

    def free(self, p_position):
        return self._grid[p_position[0]][p_position[1]].state == CELL_TYPE.FREE

    def vehicle(self, p_position):
        return self._grid[p_position[0]][p_position[1]].state == CELL_TYPE.VEHICLE

    def blocked(self, p_position):
        return self._grid[p_position[0]][p_position[1]].state == CELL_TYPE.BLOCKED
