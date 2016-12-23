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
# pylint: disable=too-few-public-methods
"""CSE classes"""
import optom.common.log


class BaseCSE(object):
    """Base class for the central optimisation entity (CSE)."""

    def __init__(self, args=None, whitelist=()):
        """
        C'tor
        :param args: argparse configuration
        :param whitelist: CSE white list for vehicles, e.g. [ "vehicle0", ... ].
                          Default: empty set (set())
        """
        if args is not None:
            self._log = optom.common.log.logger(__name__, args.loglevel, args.quiet, args.logfile)
        else:
            self._log = optom.common.log.logger(__name__)
        self._whitelist = set(whitelist)

    @property
    def whitelist(self):
        """
        Property getter of white list
        :return: frozenset of white list
        """
        return frozenset(self._whitelist)

    def allow(self, vehicle_id):
        """
        Add vehicle to white list, allowing access to OTL
        :param vehicle_id: ID of vehicle
        :return: self
        """
        self._whitelist.add(vehicle_id)
        return self

    def deny(self, vehicle_id):
        """
        Remove vehicle from white list (if element of), denying access to OTL
        :param vehicle_id: ID of vehicle
        :return: self
        """
        try:
            self._whitelist.remove(vehicle_id)
        except KeyError:
            self._log.warn("%s not in white list, no vehicle removed")
        return self

    def clear(self):
        """
        Removegi all elements from white list
        :return: self
        """
        self._whitelist.clear()
        return self


class SumoCSE(BaseCSE):
    """SUMO related class for the central optimisation entity (CSE)."""
