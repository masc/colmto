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
import random
import environment


class Vehicle(environment.GridElement):

    def __init__(self, **p_kwargs):
        self._id = p_kwargs.pop("id", None)
        self._environment = p_kwargs.pop("environment", None)
        self._vtype = p_kwargs.pop("vtype", None)
        self._speed_sigma = p_kwargs.pop("speed_sigma", 0)
        self._speed_max = p_kwargs.pop("speed_max", 0)
        self._speed_current = 0
        self._position = p_kwargs.pop("position", (None,))
        self._trajectory = []
        self._time_start = p_kwargs.pop("time_start", None)
        self._color = p_kwargs.pop("color", None)
        if p_kwargs:
            raise TypeError('Unexpected **p_kwargs: %r' % p_kwargs)

        self._trajectory = {}
        self._cycle = 0
        self._cycle_limit = 10

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
    def timestart(self):
        return self._time_start

    @property
    def speedmax(self):
        return self._speed_max

    @property
    def speedcurrent(self):
        return self._speed_current

    @property
    def speedsigma(self):
        return self._speed_sigma

    @property
    def trajectory(self):
        return self._trajectory

    @property
    def cycle(self):
        return self._cycle

    @property
    def cyclelimit(self):
        return self._cycle_limit

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, p_position):
        self._position = p_position

    @property
    def trajectory(self):
        return self._trajectory

    @trajectory.setter
    def trajectory(self, p_trajectory):
        self._trajectory = p_trajectory

    def append_trajectory(self, p_landmark):
        self._trajectory.append(p_landmark)

    def _move(self):
        pass

    def _update_position(self, p_position):
        if self._grid[p_position[0]][p_position[1]].vehicle is None and \
                        self._grid[p_position[0]][p_position[1]].state == environment.CELL_TYPE.FREE:
            if self._position != (None, None):
                self._grid[p_position[0]][p_position[1]].vehicle = None
                self._grid[p_position[0]][p_position[1]].state = environment.CELL_TYPE.FREE
            self._grid[p_position[0]][p_position[1]].vehicle = self
            self._position = (p_position[0], p_position[1])
        return self

    def run(self):
        # TODO
        print("Running vehicle", self.id, "in cycle", self.cycle)
        self._cycle += 1
        if self.cycle <= self.cyclelimit:
            return self
        return None

    def provision(self, p_id, p_time_start):
        self._id = p_id if self._id is None else self._id
        self._time_start = p_time_start if self._time_start is None else self._time_start
