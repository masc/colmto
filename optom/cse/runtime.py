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
from __future__ import print_function
from __future__ import division
from optom.common import log
from optom.environment.environment import Environment
from optom.environment.cse import CSE


class CSERuntime(object):

    def __init__(self, p_configuration):
        self._configuration = p_configuration
        self._environment = Environment()
        self._cse = CSE()

        self._environment.add_vehicle(p_vehicle_id=0, p_position=(2, 0))
        self._environment.add_vehicle(p_vehicle_id=1, p_position=(1, 0))
        self._environment.add_vehicle(p_vehicle_id=2, p_position=(0, 0))
        print(self._environment.vehicles)

    def run_scenario(self):
        print(map(lambda c: c[1].state, self._environment.grid))
        print(map(lambda c: c[0].state, self._environment.grid))
        l_runlist = [self._cse] + self.environment.vehicles.values()

        while len(l_runlist) > 1:
            l_runlist = filter(
                lambda v: v is not None,
                map(lambda v: v.run(),
                    l_runlist
                    )
            )

    @property
    def environment(self):
        return self._environment

    @property
    def vehicles(self):
        return self._vehicles

    def move(self, p_vehice_id, p_from, p_to):
        pass
