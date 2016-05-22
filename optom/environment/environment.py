# @package environment
# @cond LICENSE
# ######################################################################################
# # LGPL License                                                                       #
# #                                                                                    #
# # This file is part of the Optimisation of Overtaking Manoeuvres (OPTOM) project.                     #
# # Copyright (c) 2016, Malte Aschermann (malte.aschermann@tu-clausthal.de)            #
# # This program is free software: you can redistribute it and/or modify               #
# # it under the terms of the GNU Lesser General Public License as                     #
# # published by the Free Software Foundation, either version 3 of the                 #
# # License, or (at your option) any later version.                                    #
# #                                                                                    #
# # This program is distributed in the hope that it will be useful,                    #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of                     #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                      #
# # GNU Lesser General Public License for more details.                                #
# #                                                                                    #
# # You should have received a copy of the GNU Lesser General Public License           #
# # along with this program. If not, see http://www.gnu.org/licenses/                  #
# ######################################################################################
# @endcond
from __future__ import print_function

class Environment(object):

    def __init__(self):
        self._vehicles = {}
        self._edges = {}

    @property
    def vehicles(self):
        return self._vehicles

    @property
    def vehicle(self, p_vid):
        return self._vehicles.get(p_vid)

    @property
    def edges(self):
        return self._edges

    def edge(self, p_edgid):
        return self._edges.get(p_edgid)

    def vehicles_on_edge(self, p_edgeid):
        return filter(lambda v: v.get("edgeid") == p_edgeid, self._vehicles.items())

    def add_vehicle(self, p_vehicle):
        self._vehicles[p_vehicle.getID()] = p_vehicle


class VehicleFactory(object):
    pass

