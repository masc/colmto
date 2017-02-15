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
import math
import numpy

import optom.cse.policy


class BaseVehicle(object):
    """Base Vehicle."""

    def __init__(self, position=numpy.array((0.0, 0.0)), speed=0.0):
        """
        C'tor

        @param position position (n-tuple)
        @param speed vehicle speed
        """

        self._properties = {
            "position": numpy.array(position),
            "speed": speed,
        }

    @property
    def properties(self):
        """
        @retval vehicle properties as dictionary bundle
        """
        return self._properties

    @property
    def speed(self):
        """
        @retval current speed
        """
        return self._properties.get("speed")

    @speed.setter
    def speed(self, speed):
        """
        Sets current speed
        @param speed current speed
        """
        self._properties["speed"] = speed

    @property
    def position(self):
        """
        @retval current position
        """
        return self._properties.get("position")

    @position.setter
    def position(self, position):
        """
        Updates current position
        @param position current position
        """
        self._properties["position"] = position


class SUMOVehicle(BaseVehicle):
    """SUMO vehicle class."""

    def __init__(self, speed_max=0.0, speed_deviation=0.0, position=numpy.array((0.0, 0.0)),
                 vtype_sumo_cfg=None, vehicle_class=optom.cse.policy.SUMOPolicy.to_allowed_class(),
                 vehicle_type=None, color=numpy.array((255, 255, 0, 255))):
        """
        C'tor.

        @param speed_max
        @param speed_deviation
        @param position
        @param vtype_sumo_cfg
        @param vehicle_class
        @param vehicle_type
        @param color
        """

        super(SUMOVehicle, self).__init__(
            position=position
        )

        if isinstance(vtype_sumo_cfg, dict):
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
            "travel_time": 0.0,
            "max_speed": speed_max,
            "vehicle_type": vehicle_type,
            "time_loss": {},
            "position": {},
            "dissatisfaction": {}
        }

    @property
    def properties(self):
        """
        @retval vehicle's properties as a dict bundle
        """
        return self._properties

    @property
    def vehicle_type(self):
        """
        @retval vehicle type
        """
        return self._properties.get("vType")

    @property
    def start_time(self):
        """
        Returns start time

        @retval start time
        """
        return self._properties.get("start_time")

    @start_time.setter
    def start_time(self, start_time):
        """
        Sets start time.

        @param start_time start time
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
        @param color Color (rgba-tuple, e.g. (255, 255, 0, 255))
        """
        self._properties["color"] = numpy.array(color)

    @property
    def vehicle_class(self):
        """
        @retval SUMO vehicle class
        """
        return self._properties.get("vClass")

    @property
    def speed_max(self):
        """
        @retval self._properties.get("maxSpeed")
        """
        return self._properties.get("maxSpeed")

    @property
    def travel_time(self):
        """
        Returns current travel time

        @retval travel time
        """
        return self._travel_stats.get("travel_time")

    @property
    def travel_stats(self):
        """
        @brief Returns travel stats dictionary

        @retval self._travel_stats
        """
        return self._travel_stats

    @staticmethod
    def _dissatisfaction(time_loss, optimal_travel_time, time_loss_threshold=0.2):
        """
        Calculate driver's dissatisfaction

        $$dissatisfaction := dsat(time\\_loss, \\widehat{optimal\\_travel\\_time},
        time\\_loss\\_threshold) = \frac{1}{1+e^{\\widehat{time\\_loss}-time\\_loss}}$$

        @param time_loss time loss
        @param time_loss_threshold cut-off point of acceptable time loss
            relative to optimal travel time in [0,1]
        @param optimal_travel_time optimal travel time
        @retval dissatisfaction ([0,1] normalised)
        """
        return 1/(1+math.exp(-time_loss + optimal_travel_time * time_loss_threshold))

    def record_travel_stats(self, time_step):
        """
        @brief Write travel stats, i.e. travel time, time loss, position,
        and dissatisfaction of vehicle for a given time step.

        $$time\\_loss := travel\\_time - \frac{position}{max\\_speed}.$$
        $$dissatisfaction := dsat(time\\_loss, \\widehat{optimal\\_travel\\_time},
        time\\_loss\\_threshold) = \frac{1}{1+e^{\\widehat{time\\_loss}-time\\_loss}}$$


        @param time_step current time step

        @retval self
        """

        # current travel time
        self._travel_stats["travel_time"] = time_step - self.start_time

        # time loss
        self._travel_stats.get("time_loss")[time_step] = time_step - self.start_time \
            - self.position[0] / self.speed_max

        # position
        self._travel_stats.get("position")[time_step] = self.position

        # dissatisfaction
        self._travel_stats.get("dissatisfaction")[time_step] = self._dissatisfaction(
            self._travel_stats.get("time_loss")[time_step],
            self.position[0] / self.speed_max,
            self._properties.get("dsat_threshold")
        )

        return self

    def change_vehicle_class(self, class_name):
        """
        Change vehicle class
        @param class_name vehicle class
        @retval self
        """
        self._properties["vClass"] = class_name
        return self
