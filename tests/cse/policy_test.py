# -*- coding: utf-8 -*-
# @package tests
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
"""
optom: Test module for environment.policy.
"""
import random

import numpy
from nose.tools import assert_equal
from nose.tools import assert_is_instance

import optom.cse.policy


def test_base_policy():
    """
    Test BasePolicy class
    """
    l_base_policy = optom.cse.policy.BasePolicy(
        optom.cse.policy.BEHAVIOUR.deny
    )
    assert_is_instance(l_base_policy, optom.cse.policy.BasePolicy)


def test_sumo_policy():
    """
    Test SumoPolicy class
    """
    l_sumo_policy = optom.cse.policy.SUMOPolicy(
        optom.cse.policy.BEHAVIOUR.deny
    )
    assert_is_instance(l_sumo_policy, optom.cse.policy.SUMOPolicy)

    assert_equal(l_sumo_policy.to_disallowed_class(), "custom1")
    assert_equal(l_sumo_policy.to_allowed_class(), "custom2")


def test_sumo_null_policy():
    """
    Test SumoNullPolicy class
    """
    l_sumo_policy = optom.cse.policy.SUMONullPolicy()
    assert_is_instance(l_sumo_policy, optom.cse.policy.SUMONullPolicy)

    l_vehicles = [
        optom.environment.vehicle.SUMOVehicle() for _ in xrange(23)
    ]
    for i_vehicle in l_vehicles:
        i_vehicle.change_vehicle_class(
            random.choice(
                [
                    optom.cse.policy.SUMOPolicy.to_disallowed_class(),
                    optom.cse.policy.SUMOPolicy.to_allowed_class()
                ]
            )
        )

    l_results = l_sumo_policy.apply(l_vehicles)

    for i in xrange(len(l_vehicles)):
        assert_equal(l_vehicles[i].vehicle_class, l_results[i].vehicle_class)


def test_sumo_speed_policy():
    """
    Test SumoSpeedPolicy class
    """
    l_sumo_policy = optom.cse.policy.SUMOSpeedPolicy(speed_range=numpy.array((0., 60.)))
    assert_is_instance(l_sumo_policy, optom.cse.policy.SUMOSpeedPolicy)

    l_vehicles = [
        optom.environment.vehicle.SUMOVehicle(
            speed_max=random.randrange(0, 120)
        ) for _ in xrange(4711)
    ]

    l_results = l_sumo_policy.apply(l_vehicles)

    for i in xrange(len(l_results)):
        if 0. <= l_vehicles[i].speed_max <= 60.0:
            assert_equal(
                l_results[i].vehicle_class,
                optom.cse.policy.SUMOPolicy.to_disallowed_class()
            )
        else:
            assert_equal(
                l_results[i].vehicle_class,
                optom.cse.policy.SUMOPolicy.to_allowed_class()
            )
