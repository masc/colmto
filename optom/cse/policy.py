# -*- coding: utf-8 -*-
# @package optom.cse
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
# pylint: disable=too-few-public-methods
"""Policy related classes"""
import numpy

import optom.common.helper

BEHAVIOUR = optom.common.helper.Enum(["deny", "allow"])

SUMO_VCLASS = {
    BEHAVIOUR.allow: "custom2",
    BEHAVIOUR.deny: "custom1"
}


class BasePolicy(object):
    """Base Policy"""

    def __init__(self, default_behaviour=BEHAVIOUR.deny):
        """
        C'tor
        :param default_behaviour: Default, i.e. baseline policy.
                                  Enum of optom.cse.policy.BEHAVIOUR.deny/allow
        """
        self._behaviour = default_behaviour

    @staticmethod
    def behaviour_from_string_or_else(p_behaviour, p_or_else):
        """
        Transforms string argument of behaviour, i.e. "allow", "deny" case insensitive to
        BEHAVIOUR enum value. Otherwise return passed p_or_else argument.
        :param p_behaviour: string "allow", "deny"
        :param p_or_else: otherwise returned argument
        :return: BEHAVIOUR.allow, BEHAVIOUR.deny, p_or_else
        """
        if p_behaviour.lower() == "allow":
            return BEHAVIOUR.allow
        if p_behaviour.lower() == "deny":
            return BEHAVIOUR.deny
        return p_or_else


class SUMOPolicy(BasePolicy):
    """
    Policy class to encapsulate SUMO's 'custom2'/'custom1' vehicle classes
    for allowing/disallowing access to overtaking lane (OTL)
    """

    def __init__(self, p_behaviour=BEHAVIOUR.deny):
        """C'tor"""
        super(SUMOPolicy, self).__init__(p_behaviour)

    @staticmethod
    def to_allowed_class():
        """Get the SUMO class for allowed vehicles"""
        return SUMO_VCLASS.get(BEHAVIOUR.allow)

    @staticmethod
    def to_disallowed_class():
        """Get the SUMO class for disallowed vehicles"""
        return SUMO_VCLASS.get(BEHAVIOUR.deny)


class SUMODenyPolicy(SUMOPolicy):
    """
    Deny policy, i.e. always deny access
    """

    def __init__(self, p_behaviour=BEHAVIOUR.deny):
        """C'tor"""
        super(SUMODenyPolicy, self).__init__(p_behaviour)

    @staticmethod
    def applies_to(p_vehicle):
        """
        Test whether this policy applies to given vehicle
        :param p_vehicle: Vehicle
        :return: boolean
        """
        if p_vehicle:
            return True

        return True

    def apply(self, p_vehicles):
        """
        apply policy to vehicles
        :param p_vehicles: iterable object containing BaseVehicles, or inherited objects
        :return: List of vehicles with applied, i.e. set attributes, whether they can use otl or not
        """

        return [
            i_vehicle.change_vehicle_class(
                self.to_disallowed_class()
            ) for i_vehicle in p_vehicles
        ]


class SUMONullPolicy(SUMOPolicy):
    """
    Null policy, i.e. no restrictions: Every vehicle can use overtaking lane (OTL) depending on
    default policy
    """

    def __init__(self, p_behaviour=BEHAVIOUR.deny):
        """C'tor"""
        super(SUMONullPolicy, self).__init__(p_behaviour)

    @staticmethod
    def applies_to(p_vehicle):
        """
        Test whether this policy applies to given vehicle
        :param p_vehicle: Vehicle
        :return: boolean
        """
        if p_vehicle:
            return False

        return False

    @staticmethod
    def apply(p_vehicles):
        """
        apply policy to vehicles
        :param p_vehicles: iterable object containing BaseVehicles, or inherited objects
        :return: List of vehicles with applied, i.e. set attributes, whether they can use otl or not
        """
        return p_vehicles


class SUMOSpeedPolicy(SUMOPolicy):
    """Speed based policy: Applies to vehicles within a given speed range"""

    def __init__(self, speed_range=(0, 120), behaviour=BEHAVIOUR.deny):
        """C'tor"""
        super(SUMOSpeedPolicy, self).__init__(behaviour)
        self._speed_range = numpy.array(speed_range)

    def __str__(self):
        return "SUMOSpeedPolicy: speed_range = {}, behaviour = {}".format(
            self._speed_range, self._behaviour
        )

    def applies_to(self, p_vehicle):
        """
        Test whether this policy applies to given vehicle
        :param p_vehicle: Vehicle
        :return: boolean
        """
        if self._speed_range[0] <= p_vehicle.speed_max <= self._speed_range[1]:
            return True
        return False

    def apply(self, p_vehicles):
        """
        apply policy to vehicles
        :param p_vehicles: iterable object containing BaseVehicles, or inherited objects
        :return: List of vehicles with applied, i.e. set attributes, whether they can use otl or not
        """

        return [
            i_vehicle.change_vehicle_class(
                SUMO_VCLASS.get(self._behaviour)
            ) if self.applies_to(i_vehicle) else i_vehicle
            for i_vehicle in p_vehicles
        ]


class SUMOPositionPolicy(SUMOPolicy):
    """
    Position based policy: Applies to vehicles which are located inside a given bounding box, i.e.
    [(left_lane_0, right_lane_0) -> (left_lane_1, right_lane_1)]
    """

    def __init__(self, p_position_box=numpy.array(((0.0, 0), (100.0, 1))),
                 p_behaviour=BEHAVIOUR.deny):
        """C'tor"""
        super(SUMOPositionPolicy, self).__init__(p_behaviour)
        self._position_box = p_position_box

    def applies_to(self, p_vehicle):
        """
        Test whether this policy applies to given vehicle
        :param p_vehicle: Vehicle
        :return: boolean
        """
        if numpy.all(numpy.logical_and(self._position_box[0] <= p_vehicle.position,
                                       p_vehicle.position <= self._position_box[1])):
            return True
        return False

    def apply(self, p_vehicles):
        """
        apply policy to vehicles
        :param p_vehicles: iterable object containing BaseVehicles, or inherited objects
        :return: List of vehicles with applied, i.e. set attributes, whether they can use otl or not
        """

        return [
            i_vehicle.change_vehicle_class(
                SUMO_VCLASS.get(self._behaviour)
            ) if self.applies_to(i_vehicle) else i_vehicle
            for i_vehicle in p_vehicles
        ]
