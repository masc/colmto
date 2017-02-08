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
# pylint: disable=no-self-use
"""CSE classes"""
import optom.common.log
import optom.cse.policy


class BaseCSE(object):
    """Base class for the central optimisation entity (CSE)."""

    _log = optom.common.log.logger(__name__)
    _vehicles = set()

    def __init__(self, policies=(), args=None):
        """
        C'tor
        :param args: argparse configuration
        """
        if args is not None:
            self._log = optom.common.log.logger(__name__, args.loglevel, args.quiet, args.logfile)
        self._policies = policies

    def apply(self, vehicles):
        """
        Apply policies to vehicles
        :param vehicles: Iterable of vehicles
        :return: vehicles
        """
        for i_vehicle in vehicles:
            for i_policy in self._policies:
                if i_policy.applies_to(i_vehicle):
                    i_vehicle.change_vehicle_class(
                        optom.cse.policy.SUMOPolicy.to_disallowed_class()
                    )
                    break

        return vehicles


class SumoCSE(BaseCSE):
    """First-come-first-served CSE (basically do nothing and allow all vehicles access to OTL."""

    @staticmethod
    def update(vehicles):
        """Update vehicles"""
        return set(
            [i_v.change_vehicle_class("custom1") for i_v in vehicles]
        )
