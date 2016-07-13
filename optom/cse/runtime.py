# -*- coding: utf-8 -*-
# @package optom
# @cond LICENSE
# ######################################################################################
# # LGPL License                                                                       #
# #                                                                                    #
# # This file is part of the Optimisation of Overtaking Manoeuvres (OPTOM) project.                     #
# # Copyright (c) 2016, Malte Aschermann (malte.aschermann@tu-clausthal.de)            #
# # This program is free software: you can redistribute it and/or modify               #
# # it under the terms of the GNU Lesser General Public License as                     #
# # published by the Free Software Foundation, either version 3 of the                 #
# # License, or (at your option) any later version.                                    #
# #                                                                                    #
# # This program is distributed in the hope that it will be useful,                    #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of                     #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                      #
# # GNU Lesser General Public License for more details.                                #
# #                                                                                    #
# # You should have received a copy of the GNU Lesser General Public License           #
# # along with this program. If not, see http://www.gnu.org/licenses/                  #
# ######################################################################################
# @endcond
from __future__ import print_function
from __future__ import division
from optom.common import log
from optom.common.enum import Enum

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


class Vehicle(object):

    def __init__(self, p_vehicle_id, p_grid):
        self._vehicle_id = p_vehicle_id
        self._grid = p_grid
        self._desired_speed = 0
        self._current_speed = 0
        self._position = (None, None)


    @property
    def vehicle_id(self):
        return self._vehicle_id

    @property
    def position(self):
        return self._position

    def update_position(self, p_position):
        if self._grid[p_position[0]][p_position[1]].vehicle is None and \
                        self._grid[p_position[0]][p_position[1]].state == CELL_TYPE.FREE:
            if self._position != (None,None):
                self._grid[p_position[0]][p_position[1]].vehicle = None
                self._grid[p_position[0]][p_position[1]].state = CELL_TYPE.FREE
            self._grid[p_position[0]][p_position[1]].vehicle = self
            self._position = (p_position[0], p_position[1])
        return self

    def run(self):
        pass


class Environment(object):

    def __init__(self):
        self._grid = [[Cell(), Cell(CELL_TYPE.BLOCKED)] for _ in xrange(10)] + \
                     [[Cell(), Cell()] for _ in xrange(10)] + \
                     [[Cell(), Cell(CELL_TYPE.BLOCKED)] for _ in xrange(10)]
        self._vehicle_map = {}

    @property
    def grid(self):
        return self._grid

    @property
    def vehicle_map(self):
        return self._vehicle_map

    def isfree(self, p_position):
        return self._grid[p_position[0]][p_position[1]].state == CELL_TYPE.FREE

    def isvehicle(self, p_position):
        return self._grid[p_position[0]][p_position[1]].state == CELL_TYPE.VEHICLE

    def isblocked(self, p_position):
        return self._grid[p_position[0]][p_position[1]].state == CELL_TYPE.BLOCKED


class Runtime(object):

    def run_scenario(self):
        print(map(lambda c: c[1].state, self._environment.grid))
        print(map(lambda c: c[0].state, self._environment.grid))

    def __init__(self, p_configuration):
        self._configuration = p_configuration
        self._environment = Environment()
        self.add_vehicle("0", (2,0))
        self.add_vehicle("1", (1,0))
        self.add_vehicle("2", (0,0))

    def add_vehicle(self, p_vehicle_id, p_position):
        if self._environment.isfree(p_position) and p_vehicle_id not in self._environment.vehicle_map:
            self._environment.vehicle_map[p_vehicle_id] = Vehicle(p_vehicle_id, self._environment.grid).update_position(p_position)

    def move(self, p_vehice_id, p_from, p_to):
        pass