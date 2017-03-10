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
from nose.tools import assert_raises
from nose.tools import assert_in

import optom.cse.cse
import optom.cse.policy
import optom.common.helper
import optom.environment.vehicle


def test_base_cse():
    """
    Test BaseCSE class
    """
    assert_is_instance(optom.cse.cse.BaseCSE(), optom.cse.cse.BaseCSE)
    assert_is_instance(
        optom.cse.cse.BaseCSE(
            optom.common.helper.Namespace(
                loglevel="debug", quiet=False, logfile="foo.log"
            )
        ),
        optom.cse.cse.BaseCSE
    )


def test_sumo_cse():
    """
    Test SumoCSE class
    """
    assert_is_instance(
        optom.cse.cse.SumoCSE(
            optom.common.helper.Namespace(
                loglevel="debug", quiet=False, logfile="foo.log"
            )
        ),
        optom.cse.cse.SumoCSE
    )

    l_policy_speed = optom.cse.policy.SUMOSpeedPolicy(speed_range=numpy.array((0., 80.)))
    l_policy_position = optom.cse.policy.SUMOPositionPolicy(
        position_bbox=numpy.array(((0., 0), (64.0, 1)))
    )
    l_subpolicy_speed = optom.cse.policy.SUMOSpeedPolicy(speed_range=numpy.array((0., 60.)))
    l_policy_position.add_vehicle_policy(l_subpolicy_speed)

    l_sumo_cse = optom.cse.cse.SumoCSE().add_policy(l_policy_speed).add_policy(l_policy_position)

    assert_is_instance(l_sumo_cse, optom.cse.cse.SumoCSE)
    assert_is_instance(l_sumo_cse.policies, tuple)
    assert_in(l_policy_position, l_sumo_cse.policies)
    assert_in(l_policy_position, l_sumo_cse.policies)

    with assert_raises(AttributeError):
        l_sumo_cse.add_policy("foo")

    l_vehicles = [
        optom.environment.vehicle.SUMOVehicle(
            speed_max=random.randrange(0, 250)
        ) for _ in xrange(2342)
    ]
    for i_vehicle in l_vehicles:
        i_vehicle.position = numpy.array((random.randrange(0, 120), random.randint(0, 1)))

    l_sumo_cse.apply(l_vehicles)

    for i, i_result in enumerate(l_vehicles):
        if (0 <= l_vehicles[i].position[0] <= 64.0 and 0 <= l_vehicles[i].position[1] <= 1
                and 0 <= l_vehicles[i].speed_max <= 60.0) \
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

    assert_equal(
        optom.cse.cse.SumoCSE().add_policies_from_cfg(None).policies,
        tuple()
    )

    l_sumo_cse = optom.cse.cse.SumoCSE().add_policies_from_cfg(
        [
            {
                "type": "SUMOSpeedPolicy",
                "behaviour": "deny",
                "args": {
                    "speed_range": (0., 30/3.6)
                }
            },
            {
                "type": "SUMOPositionPolicy",
                "behaviour": "deny",
                "args": {
                    "position_bbox": ((1350., -2.), (2500., 2.))
                },
                "vehicle_policies": {
                    "rule": "any",
                    "policies": [
                        {
                            "type": "SUMOSpeedPolicy",
                            "behaviour": "deny",
                            "args": {
                                "speed_range": (0., 85/3.6)
                            },
                        }
                    ]
                }
            }
        ]
    )

    assert_is_instance(l_sumo_cse.policies[0], optom.cse.policy.SUMOSpeedPolicy)
    assert_is_instance(l_sumo_cse.policies[1], optom.cse.policy.SUMOPositionPolicy)
    assert_is_instance(l_sumo_cse.policies[1].vehicle_policies[0], optom.cse.policy.SUMOSpeedPolicy)
