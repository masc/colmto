# -*- coding: utf-8 -*-
# @package optom
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of Overtaking Manoeuvres project.   #
# # Copyright (c) 2017, Malte Aschermann (malte.aschermann@tu-clausthal.de)   #
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

    def __init__(self):
        """
        C'tor

        @param position position (n-tuple)
        @param speed vehicle speed
        """

        self._properties = {
            "position": numpy.array((0.0, 0.0)),
            "speed": 0.0,
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

    @property
    def position(self):
        """
        @retval current position
        """
        return self._properties.get("position")


class SUMOVehicle(BaseVehicle):
    """SUMO vehicle class."""

    def __init__(self,
                 vehicle_type=None,
                 vtype_sumo_cfg=None,
                 speed_deviation=0.0,
                 speed_max=0.0):
        """
        C'tor.

        @param vehicle_type
        @param vtype_sumo_cfg
        @param speed_deviation
        @param speed_max
        """

        super(SUMOVehicle, self).__init__()

        if isinstance(vtype_sumo_cfg, dict):
            self._properties.update(vtype_sumo_cfg)

        self._properties.update(
            {
                "color": numpy.array((255, 255, 0, 255)),
                "start_time": 0.0,
                "speedDev": speed_deviation,
                "maxSpeed": speed_max,
                "vType": vehicle_type,
                "vClass": optom.cse.policy.SUMOPolicy.to_allowed_class(),
                "grid_position": numpy.array((0, 0))
            }
        )

        self._travel_stats = {
            "start_time": 0.0,
            "travel_time": 0.0,
            "vehicle_type": vehicle_type,
            "grid": {
                "pos_x": [],
                "pos_y": [],
                "time_loss": [],
                "speed": [],
                "dissatisfaction": []
            },
            "step": {
                "number": [],
                "pos_x": [],
                "pos_y": [],
                "time_loss": [],
                "speed": [],
                "dissatisfaction": []
            }
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
        r"""Calculate driver's dissatisfaction.
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
        r"""Record travel statistics to vehicle.
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

        # current step number
        self._travel_stats.get("step").get("number").append(time_step)

        # position
        self._travel_stats.get("step").get("pos_x").append(self.position[0])
        self._travel_stats.get("step").get("pos_y").append(self.position[1])

        # grid based stats
        # check whether vehicle stayed in this grid cell
        if len(self._travel_stats.get("grid").get("pos_x")) > 0 \
            and len(self._travel_stats.get("grid").get("pos_y")) > 0 \
            and isinstance(self._travel_stats.get("grid").get("pos_x")[-1], list) \
                and isinstance(self._travel_stats.get("grid").get("pos_y")[-1], list) \
                and self._travel_stats.get("grid").get("pos_x")[-1][0] == self.grid_position[0] \
                and self._travel_stats.get("grid").get("pos_y")[-1][0] == self.grid_position[1]:
            self._travel_stats.get("grid").get("pos_x")[-1].append(self.grid_position[0])
            self._travel_stats.get("grid").get("pos_y")[-1].append(self.grid_position[1])
            self._travel_stats.get("grid").get("speed")[-1].append(self.speed)
            self._travel_stats.get("grid").get("time_loss")[-1].append(
                time_step - self.start_time - self.position[0] / self.speed_max
            )
            self._travel_stats.get("grid").get("dissatisfaction")[-1].append(
                self._dissatisfaction(
                    time_step - self.start_time - self.position[0] / self.speed_max,
                    self.position[0] / self.speed_max,
                    self._properties.get("dsat_threshold")
                )
            )

        else:
            self._travel_stats.get("grid").get("pos_x").append([self.grid_position[0]])
            self._travel_stats.get("grid").get("pos_y").append([self.grid_position[1]])
            self._travel_stats.get("grid").get("speed").append([self.speed])
            self._travel_stats.get("grid").get("time_loss").append(
                [time_step - self.start_time - self.position[0] / self.speed_max]
            )
            self._travel_stats.get("grid").get("dissatisfaction").append(
                [
                    self._dissatisfaction(
                        time_step - self.start_time - self.position[0] / self.speed_max,
                        self.position[0] / self.speed_max,
                        self._properties.get("dsat_threshold")
                    )
                ]
            )

        # step based stats
        self._travel_stats.get("step").get("time_loss").append(
            time_step - self.start_time - self.position[0] / self.speed_max
        )

        self._travel_stats.get("step").get("speed").append(self.speed)

        self._travel_stats.get("step").get("dissatisfaction").append(
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

    def update(self, position, lane_index, speed):
        """
        Update current properties of vehicle providing data acquired from TraCI call.

        For the grid cell the vehicle is in, take the global position in x-direction divided by grid
        cell size and int-rounded. For the y-coordinate take the lane index.
        NOTE: We assume a fixed grid cell size of 4 meters. This has to be set via cfg in future.

        @param position: tuple TraCI provided position
        @param lane_index: int TraCI provided lane index
        @param speed: float TraCI provided speed
        @retval self Vehicle reference
        """

        # set current position
        self._properties["position"] = numpy.array(position)
        # set current grid position
        self._properties["grid_position"] = numpy.array(
            (
                int(round(position[0]/4.)-1),
                int(lane_index)
            )
        )
        # set speed
        self._properties["speed"] = speed

        return self
