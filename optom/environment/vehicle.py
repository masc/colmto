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
"""Vehicle classes for storing vehicle data/attributes/states."""
import numpy

import optom.cse.policy


class BaseVehicle(object):
    """Base Vehicle."""

    def __init__(self, speed_max=0.0, speed_current=0.0, position=numpy.array([0.0, 0])):
        self._speed_max = speed_max
        self._speed_current = speed_current
        self._position = position

    @property
    def properties(self):
        """Returns vehicle properties as dictionary bundle"""
        return {
            "position": self.position,
            "speed_current": self.speed_current,
            "speed_max": self.speed_max
        }

    @property
    def speed_max(self):
        """Returns maximum capable velocity of vehicle."""
        return self._speed_max

    @speed_max.setter
    def speed_max(self, speed):
        """Sets maximum speed."""
        self._speed_max = speed

    @property
    def speed_current(self):
        """Returns current speed."""
        return self._speed_current

    @speed_current.setter
    def speed_current(self, speed):
        """Sets current speed."""
        self._speed_current = speed

    @property
    def position(self):
        """Returns current position."""
        return self._position

    @position.setter
    def position(self, p_position):
        """Updates current position."""
        self._position = p_position


class SUMOVehicle(BaseVehicle):
    """SUMO vehicle class."""

    def __init__(self, **kwargs):
        """
        C'tor.
        :param kwargs: Recognised arguments (with default values) are
                       speed_max=0.0, speed_current=0.0, position=(None,), speed_deviation=0.0,
                       vtype=None, vtype_sumo_cfg={}, color=(255, 255, 0, 255), start_time=0.0
        """

        self._vtype = kwargs.pop("vtype", None)
        self._vtype_sumo_cfg = kwargs.pop("vtype_sumo_cfg", {})
        self._color = kwargs.pop("color", (255, 255, 0, 255))
        self._speed_deviation = kwargs.pop("speed_deviation", 0.0)
        self._start_time = kwargs.pop("start_time", 0.0)
        self._vehicle_class = kwargs.pop(
            "vehicle_class", optom.cse.policy.SUMOPolicy.to_allowed_class()
        )

        super(SUMOVehicle, self).__init__(**kwargs)

        self._travel_times = {}
        self._time_losses = {}

    @property
    def properties(self):
        """Returns vehicle's properties as a dict bundle."""
        return {
            "position": self._position,
            "speed_current": self._speed_current,
            "speed_max": self._speed_max,
            "vtype": self.vtype,
            "vtype_sumo_cfg": self.vtype_sumo_cfg,
            "color": self._color,
            "speed_deviation": self._speed_deviation,
            "travel_times": self._travel_times,
            "time_losses": self._time_losses,
            "start_time": self._start_time,
            "vehicle_class": self._vehicle_class
        }

    @property
    def vtype(self):
        """Return vehicle type."""
        return self._vtype

    @property
    def vtype_sumo_cfg(self):
        """
        Convert values of vtype config to str for sumo xml handling and return cfg.
        """
        return {
            attr: str(value) for (attr, value) in self._vtype_sumo_cfg.iteritems()
        }

    @property
    def color(self):
        """Return color."""
        return self._color

    @color.setter
    def color(self, p_color):
        """Update color."""
        self._color = p_color

    @property
    def speed_deviation(self):
        """Return speed deviation."""
        return self._speed_deviation

    @property
    def start_time(self):
        """Return vehicle's start time."""
        return self._start_time

    @start_time.setter
    def start_time(self, p_start_time):
        """Set start time of vehicle."""
        self._start_time = p_start_time

    @property
    def travel_times(self):
        """Return travel times."""
        return self._travel_times

    @property
    def time_losses(self):
        """Return time losses."""
        return self._time_losses

    @property
    def vehicle_class(self):
        """Return SUMO vehicle class"""
        return self._vehicle_class

    def change_vehicle_class(self, p_class_name):
        """Change vehicle class"""
        self._vehicle_class = p_class_name
        return self
