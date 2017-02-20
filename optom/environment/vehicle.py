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
import collections

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
        @retval current speed at time step
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
                "vClass": vehicle_class,
                "grid_position": (0, 0)
            }
        )

        self._travel_stats = {
            "start_time": 0.0,
            "travel_time": 0.0,
            "vehicle_type": vehicle_type,
            "grid_cell": collections.defaultdict(dict),
                #{
                # "index": collections.defaultdict(list),
                # "time_loss": collections.defaultdict(list),
                # "speed": collections.defaultdict(list),
                # "dissatisfaction": collections.defaultdict(list)
                #},
            "step": collections.defaultdict(dict)
                #{
                # "number": [],
                # "time_loss": [],
                # "position": [],
                # "speed": [],
                # "dissatisfaction": []
                #}
        }

    @property
    def grid_position(self):
        """
        @retval current grid position
        """
        return self._properties.get("grid_position")

    @grid_position.setter
    def grid_position(self, position):
        """
        Updates current position
        @param position current grid position
        """
        self._properties["grid_position"] = numpy.array(position, dtype=int)

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
        """Calculate driver's dissatisfaction.
        Calculate driver's dissatisfaction.
        \f{eqnarray*}{
            TT &:=& \text{travel time}, \\
            TT^{*} &:=& \text{optimal travel time}, \\
            TL &:=& \text{time loss}, \\
            TLT &:=& \text{time loss threshold}, \\
            \text{dissatisfaction} &:=& dsat(TL, TT^{*}, TLT) \\
            &=&\frac{1}{1+e^{-TL + TLT \cdot TT^{*}}}.
        \f}
        @param time_loss time loss
        @param time_loss_threshold cut-off point of acceptable time loss
            relative to optimal travel time in [0,1]
        @param optimal_travel_time optimal travel time
        @retval dissatisfaction ([0,1] normalised)
        """
        return 1/(1+math.exp(-time_loss + time_loss_threshold * optimal_travel_time))

    def record_travel_stats(self, time_step):
        """Record travel statistics to vehicle.
        Write travel stats, i.e. travel time, time loss, position,
        and dissatisfaction of vehicle for a given time step into self._travel_stats
        \f{eqnarray*}{
            TT &:=& \text{travel time}, \\
            TT^{*} &:=& \text{optimal travel time}, \\
            TL &:=& \text{time loss}, \\
            TLT &:=& \text{time loss threshold}, \\
            \widehat{v} &:=& \text{maximum speed of vehicle}, \\
            \text{dissatisfaction} &:=& dsat(TL, TT^{*}, TLT) \\
            &=&\frac{1}{1+e^{-TL + TLT \cdot TT^{*}}}.
        \f}
        @param time_step current time step
        @retval self
        """

        # update current travel time
        self._travel_stats["travel_time"] = time_step - self.start_time

        # time losses
        self._travel_stats.get("step")[time_step]["time_loss"] \
            = time_step - self.start_time - self.position[0] / self.speed_max

        if self._travel_stats.get("grid_cell")[tuple(self.grid_position)].get("time_loss") is None:
            self._travel_stats.get("grid_cell")[tuple(self.grid_position)]["time_loss"] \
                = [time_step - self.start_time - self.position[0] / self.speed_max]
        else:
            self._travel_stats.get("grid_cell").get(tuple(self.grid_position)).get("time_loss").append(
                time_step - self.start_time - self.position[0] / self.speed_max
            )

        # position
        self._travel_stats.get("step")[time_step]["position"] = self.position

        # speed
        self._travel_stats.get("step")[time_step]["speed"] = self.speed
        if self._travel_stats.get("grid_cell")[tuple(self.grid_position)].get("speed") is None:
            self._travel_stats.get("grid_cell")[tuple(self.grid_position)]["speed"] = [self.speed]
        else:
            self._travel_stats.get("grid_cell")[tuple(self.grid_position)].get("speed").append(self.speed)

        # dissatisfaction
        self._travel_stats.get("step")[time_step]["dissatisfaction"] = self._dissatisfaction(
                time_step - self.start_time - self.position[0] / self.speed_max,
                self.position[0] / self.speed_max,
                self._properties.get("dsat_threshold")
        )
        if self._travel_stats.get("grid_cell")[tuple(self.grid_position)].get("dissatisfaction") is None:
            self._travel_stats.get("grid_cell")[tuple(self.grid_position)]["dissatisfaction"] = [
                self._dissatisfaction(
                    time_step - self.start_time - self.position[0] / self.speed_max,
                    self.position[0] / self.speed_max,
                    self._properties.get("dsat_threshold")
                )
            ]
        else:
            self._travel_stats.get("grid_cell")[tuple(self.grid_position)].get("dissatisfaction").append(
                self._dissatisfaction(
                    time_step - self.start_time - self.position[0] / self.speed_max,
                    self.position[0] / self.speed_max,
                    self._properties.get("dsat_threshold")
                )
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
