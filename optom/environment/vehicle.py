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


class BaseVehicle(object):

    def __init__(self, p_kwargs):
        self._position = p_kwargs.pop("position", (None,))
        self._speed_max = p_kwargs.pop("speed_max", 0)
        if p_kwargs:
            raise TypeError('Unexpected **p_kwargs: %r' % p_kwargs)
        self._speed = 0

        self._dict = {
            "position": self.position,
            "speed": self.speed,
            "speed_max": self.speed_max
        }

    @property
    def dict(self):
        return self._dict

    @property
    def speed_max(self):
        return self._speed_max

    @property
    def speed(self):
        return self._speed

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, p_position):
        self._position = p_position


class SUMOVehicle(BaseVehicle):

    def __init__(self, **p_kwargs):
        self._vtype = p_kwargs.pop("vtype", None)
        self._vtype_sumo_attr = p_kwargs.pop("vtype_sumo_attr", None)
        self._color = p_kwargs.pop("color", None)
        self._speed_deviation = p_kwargs.pop("speed_deviation", 0.0)

        super(SUMOVehicle, self).__init__(p_kwargs)

        self._start_time = 0
        self._travel_times = {}
        self._time_losses = {}

        self._dict.update({
            "vtype": self.vtype,
            "vtype_sumo_attr": self.vtype_sumo_attr,
            "color": self.color,
            "speed_deviation": self.speed_deviation,
            "travel_times": self.travel_times,
            "time_losses": self.time_losses,
            "start_time": self.start_time
        })

    @property
    def vtype(self):
        return self._vtype

    @property
    def vtype_sumo_attr(self):
        return self._vtype_sumo_attr

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, p_color):
        self._color = p_color

    @property
    def speed_deviation(self):
        return self._speed_deviation

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, p_start_time):
        self._start_time = p_start_time

    @property
    def travel_times(self):
        return self._travel_times

    @property
    def time_losses(self):
        return self._time_losses


