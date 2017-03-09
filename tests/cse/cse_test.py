# -*- coding: utf-8 -*-
# @package tests
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of 2+1 Manoeuvres project.          #
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
"""
optom: Test module for environment.cse.
"""
import random

import numpy
from nose.tools import assert_equal
from nose.tools import assert_is_instance

import optom.cse.cse
import optom.cse.policy
import optom.environment.vehicle


def test_base_cse():
    """
    Test BaseCSE class
    """
    l_base_cse = optom.cse.cse.BaseCSE()
    assert_is_instance(l_base_cse, optom.cse.cse.BaseCSE)


def test_sumo_cse():
    """
    Test SumoCSE class
    """
    l_sumo_cse = optom.cse.cse.SumoCSE().add_policy(
        optom.cse.policy.SUMOSpeedPolicy(speed_range=numpy.array((0., 80.))),
    ).add_policy(
        optom.cse.policy.SUMOPositionPolicy(position_bbox=numpy.array(((0., 0), (64.0, 1))))
    )
    assert_is_instance(l_sumo_cse, optom.cse.cse.SumoCSE)

    l_vehicles = [
        optom.environment.vehicle.SUMOVehicle(
            speed_max=random.randrange(0, 250)
        ) for _ in xrange(2342)
    ]
    for i_vehicle in l_vehicles:
        i_vehicle.position = numpy.array((random.randrange(0, 120), random.randint(0, 1)))

    l_sumo_cse.apply(l_vehicles)

    for i, i_result in enumerate(l_vehicles):
        if 0 <= l_vehicles[i].position[0] <= 64.0 and 0 <= l_vehicles[i].position[1] <= 1 \
                or 0 <= l_vehicles[i].speed_max <= 80.0:
            assert_equal(
                i_result.vehicle_class,
                optom.cse.policy.SUMOPolicy.to_disallowed_class()
            )
        else:
            assert_equal(
                i_result.vehicle_class,
                optom.cse.policy.SUMOPolicy.to_allowed_class()
            )
