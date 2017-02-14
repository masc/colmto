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

    def __init__(self, speed_max=0.0, position=numpy.array((0.0, 0.0)), speed_current=0.0):
        """C'tor"""
        self._properties = {
            "position": position,
            "speed_current": speed_current,
            "speed_max": speed_max,
        }

    @property
    def properties(self):
        """
        Returns:
            vehicle properties as dictionary bundle
        """
        return self._properties

    @property
    def speed_max(self):
        """
        Returns:
            maximum capable velocity of vehicle
        """
        return self._properties.get("speed_max")

    @speed_max.setter
    def speed_max(self, speed):
        """
        Sets maximum speed.

        Args:
            speed_max: maximum desired or capable speed
        """
        self._properties["speed_max"] = speed

    @property
    def speed_current(self):
        """
        Returns:
             current speed
        """
        return self._properties.get("speed_current")

    @speed_current.setter
    def speed_current(self, speed):
        """
        Sets current speed
        Args:
            speed: current speed
        """
        self._properties["speed_current"] = speed

    @property
    def position(self):
        """
        Returns:
             current position
        """
        return self._properties.get("position")

    @position.setter
    def position(self, position):
        """
        Updates current position
        Args:
            position: current position
        """
        self._properties["position"] = position


class SUMOVehicle(BaseVehicle):
    """SUMO vehicle class."""

    def __init__(self, speed_max=0.0, position=numpy.array((0.0, 0)), speed_deviation=0.0,
                 vehicle_type=None, vehicle_class=optom.cse.policy.SUMOPolicy.to_allowed_class(),
                 vtype_sumo_cfg=None, color=numpy.array((255, 255, 0, 255))):
        """
        C'tor.
        Args:
            speed_max:
            position:
            speed_deviation:
            vehicle_type:
            vehicle_class:
            vtype_sumo_cfg:
            color:
        """

        super(SUMOVehicle, self).__init__(
            speed_max=speed_max,
            position=position,
        )

        self._properties.update(
            {
                "vehicle_type": vehicle_type,
                "vtype_sumo_cfg": vtype_sumo_cfg,
                "color": color,
                "speed_deviation": speed_deviation,
                "start_time": 0.0,
                "vehicle_class": vehicle_class,
            }
        )

    @property
    def properties(self):
        """
        Returns:
             vehicle's properties as a dict bundle
        """
        return self._properties

    @property
    def vehicle_type(self):
        """
        Returns:
             vehicle type
        """
        return self._properties.get("vehicle_type")

    @property
    def vtype_sumo_cfg(self):
        """
        Convert values of vehicle_type config to str for sumo xml handling and return cfg
        Returns:
            sumo config attributes
        """
        return {
            attr: str(value) for (attr, value) in self._properties.get("vtype_sumo_cfg").iteritems()
        } if self._properties.get("vtype_sumo_cfg") is not None else {}

    @property
    def color(self):
        """
        Returns:
            color
        """
        return self._properties.get("color")

    @color.setter
    def color(self, color):
        """
        Update color
        Args:
            color: Color
        """
        self._properties["color"] = numpy.array(color)

    @property
    def speed_deviation(self):
        """
        Returns:
             speed deviation
        """
        return self._properties.get("speed_deviation")

    @property
    def start_time(self):
        """
        Returns:
             vehicle's start time
        """
        return self._properties.get("start_time")

    @start_time.setter
    def start_time(self, start_time):
        """
        Set start time of vehicle
        Args:
            start_time: start time
        """
        self._properties["start_time"] = start_time

    @property
    def vehicle_class(self):
        """
        Returns:
             SUMO vehicle class
        """
        return self._properties.get("vehicle_class")

    def change_vehicle_class(self, class_name):
        """
        Change vehicle class
        Args:
            class_name: vehicle class
        Returns:
            self
        """
        self._properties["vehicle_class"] = class_name
        return self
