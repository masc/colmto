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

    def __init__(self, position=numpy.array((0.0, 0.0)), speed=0.0):
        """C'tor"""
        self._properties = {
            "position": position,
            "speed": speed,
        }

    @property
    def properties(self):
        """
        Returns:
            vehicle properties as dictionary bundle
        """
        return self._properties

    @property
    def speed(self):
        """
        Returns:
             current speed
        """
        return self._properties.get("speed")

    @speed.setter
    def speed(self, speed):
        """
        Sets current speed
        Args:
            speed: current speed
        """
        self._properties["speed"] = speed

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

    def __init__(self, speed_max=0.0, speed_deviation=0.0, position=numpy.array((0.0, 0.0)),
                 vtype_sumo_cfg=None, vehicle_class=optom.cse.policy.SUMOPolicy.to_allowed_class(),
                 vehicle_type=None, color=numpy.array((255, 255, 0, 255))):
        """
        C'tor.
        Args:
            speed_max:
            speed_deviation:
            position:
            vtype_sumo_cfg:
            vehicle_class:
            vehicle_type:
            color:
        """

        super(SUMOVehicle, self).__init__(
            position=position
        )

        if type(vtype_sumo_cfg) is dict:
            self._properties.update(vtype_sumo_cfg)

        self._properties.update(
            {
                "color": color,
                "start_time": 0.0,
                "speedDev": speed_deviation,
                "maxSpeed": speed_max,
                "vType": vehicle_type,
                "vClass": vehicle_class
            }
        )

        self._travel_stats = {
            "start_time": 0.0,
            "max_speed": speed_max,
            "vehicle_type": vehicle_type,
            "time_loss": {},
            "position": {}
        }

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
        return self._properties.get("vType")

    @property
    def start_time(self):
        """
        Returns:
            start time
        """
        return self._properties.get("start_time")

    @start_time.setter
    def start_time(self, start_time):
        """
        Sets start time.

        Args:
            start_time: start time
        """
        self._properties["start_time"] = start_time

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
    def vehicle_class(self):
        """
        Returns:
             SUMO vehicle class
        """
        return self._properties.get("vClass")

    @property
    def speed_max(self):
        """
        Returns:
            maximum speed
        """
        return self._properties.get("maxSpeed")

    @property
    def travel_stats(self):
        """
        Returns travel stats dictionary

        Returns:
            travel stats
        """
        return self._travel_stats

    def record_travel_stats(self, time_step):
        """
        Write travel stats, i.e. time losses and position of vehicle for a given time step.

        $$time\\_loss := travel\\_time - \frac{position}{max\\_speed}.$$

        Args:
            time_step: current time step

        Returns:
            self
        """

        self._travel_stats.get("time_loss")[time_step] = time_step - self.start_time \
            - self.position[0]/self.speed_max
        self._travel_stats.get("position")[time_step] = self.position

        return self

    def change_vehicle_class(self, class_name):
        """
        Change vehicle class
        Args:
            class_name: vehicle class
        Returns:
            self
        """
        self._properties["vClass"] = class_name
        return self
