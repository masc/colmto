# -*- coding: utf-8 -*-
# @package tests
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Cooperative Lane Management and Traffic flow     #
# # Optimisation project.                                                     #
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
colmto: Test module for environment.policy.
"""
import random

import numpy

from nose.tools import assert_equal
from nose.tools import assert_false
from nose.tools import assert_is_instance
from nose.tools import assert_raises
from nose.tools import assert_true
from nose.tools import assert_tuple_equal

import colmto.cse.policy
import colmto.environment.vehicle


def test_base_policy():
    """
    Test BasePolicy class
    """
    l_base_policy = colmto.cse.policy.BasePolicy(
        colmto.cse.policy.BEHAVIOUR.deny
    )
    assert_is_instance(l_base_policy, colmto.cse.policy.BasePolicy)


def test_behaviourfromstringorelse():
    """Test colmto.cse.policy.BasePolicy.behaviour_from_string_or_else."""
    assert_equal(
        colmto.cse.policy.BasePolicy(
            colmto.cse.policy.BEHAVIOUR.deny
        ).behaviour_from_string_or_else("Allow", "foo"),
        colmto.cse.policy.BEHAVIOUR.allow
    )
    assert_equal(
        colmto.cse.policy.BasePolicy(
            colmto.cse.policy.BEHAVIOUR.deny
        ).behaviour_from_string_or_else("Deny", "foo"),
        colmto.cse.policy.BEHAVIOUR.deny
    )
    assert_equal(
        colmto.cse.policy.BasePolicy(
            colmto.cse.policy.BEHAVIOUR.deny
        ).behaviour_from_string_or_else("Meh", "foo"),
        "foo"
    )


def test_sumo_policy():
    """
    Test SumoPolicy class
    """
    l_sumo_policy = colmto.cse.policy.SUMOPolicy(
        colmto.cse.policy.BEHAVIOUR.deny
    )
    assert_is_instance(l_sumo_policy, colmto.cse.policy.SUMOPolicy)

    assert_equal(l_sumo_policy.to_disallowed_class(), "custom1")
    assert_equal(l_sumo_policy.to_allowed_class(), "custom2")


def test_sumo_null_policy():
    """
    Test SumoNullPolicy class
    """
    l_sumo_policy = colmto.cse.policy.SUMONullPolicy()
    assert_is_instance(l_sumo_policy, colmto.cse.policy.SUMONullPolicy)

    l_vehicles = [
        colmto.environment.vehicle.SUMOVehicle() for _ in xrange(23)
        ]
    for i_vehicle in l_vehicles:
        i_vehicle.change_vehicle_class(
            random.choice(
                [
                    colmto.cse.policy.SUMOPolicy.to_disallowed_class(),
                    colmto.cse.policy.SUMOPolicy.to_allowed_class()
                ]
            )
        )

    l_results = l_sumo_policy.apply(l_vehicles)

    for i in xrange(len(l_vehicles)):
        assert_equal(l_vehicles[i].vehicle_class, l_results[i].vehicle_class)
        assert_false(l_sumo_policy.applies_to(l_vehicles[i]))

    with assert_raises(TypeError):
        l_sumo_policy.applies_to("foo")


def test_sumo_vtype_policy():
    """Test SUMOVTypePolicy class"""
    assert_is_instance(colmto.cse.policy.SUMOVTypePolicy(), colmto.cse.policy.SUMOVTypePolicy)

    assert_equal(
        str(
            colmto.cse.policy.SUMOVTypePolicy(
                vehicle_type="passenger",
                behaviour=colmto.cse.policy.BEHAVIOUR.deny
            ).add_vehicle_policy(
                colmto.cse.policy.SUMOPositionPolicy(
                    position_bbox=((0., -1.), (100., 1.))
                )
            )
        ),
        "<class 'colmto.cse.policy.SUMOVTypePolicy'>: vehicle_type = passenger, behaviour = 0, "
        "subpolicies: []: <class 'colmto.cse.policy.SUMOPositionPolicy'>: "
        "position_bbox = ((0.0, -1.0), (100.0, 1.0)), behaviour = 0, subpolicies: []: "
    )

    assert_true(
        colmto.cse.policy.SUMOVTypePolicy(
            vehicle_type="passenger",
            behaviour=colmto.cse.policy.BEHAVIOUR.deny
        ).applies_to(
            colmto.environment.vehicle.SUMOVehicle(
                vehicle_type="passenger"
            )
        )
    )

    assert_false(
        colmto.cse.policy.SUMOVTypePolicy(
            vehicle_type="truck",
            behaviour=colmto.cse.policy.BEHAVIOUR.allow
        ).applies_to(
            colmto.environment.vehicle.SUMOVehicle(
                vehicle_type="passenger"
            )
        )
    )

    assert_equal(
        colmto.cse.policy.SUMOVTypePolicy(
            vehicle_type="passenger",
            behaviour=colmto.cse.policy.BEHAVIOUR.deny
        ).apply([colmto.environment.vehicle.SUMOVehicle(vehicle_type="passenger")])[0].vehicle_class,
        "custom1"
    )

    assert_equal(
        colmto.cse.policy.SUMOVTypePolicy(
            vehicle_type="passenger",
            behaviour=colmto.cse.policy.BEHAVIOUR.allow
        ).apply([colmto.environment.vehicle.SUMOVehicle(vehicle_type="passenger")])[0].vehicle_class,
        "custom2"
    )

    assert_equal(
        colmto.cse.policy.SUMOVTypePolicy(
            vehicle_type="truck",
            behaviour=colmto.cse.policy.BEHAVIOUR.deny
        ).apply([colmto.environment.vehicle.SUMOVehicle(vehicle_type="passenger")])[0].vehicle_class,
        "custom2"
    )


def test_sumo_extendable_policy():
    """Test SUMOExtendablePolicy class"""
    with assert_raises(TypeError):
        colmto.cse.policy.SUMOExtendablePolicy(
            vehicle_policies=[colmto.cse.policy.SUMONullPolicy()],
            rule="any"
        )

    with assert_raises(ValueError):
        colmto.cse.policy.SUMOExtendablePolicy(
            vehicle_policies=[colmto.cse.policy.SUMOSpeedPolicy()],
            rule="foo"
        )

    l_sumo_policy = colmto.cse.policy.SUMOExtendablePolicy(
        vehicle_policies=[colmto.cse.policy.SUMOSpeedPolicy()],
        rule="any"
    )

    assert_equal(l_sumo_policy.rule, "any")
    l_sumo_policy.rule = "all"
    assert_equal(l_sumo_policy.rule, "all")

    with assert_raises(ValueError):
        l_sumo_policy.rule = "foo"

    l_sumo_policy.add_vehicle_policy(colmto.cse.policy.SUMOPositionPolicy())

    with assert_raises(TypeError):
        l_sumo_policy.add_vehicle_policy(colmto.cse.policy.SUMONullPolicy())

    l_sumo_policy = colmto.cse.policy.SUMOExtendablePolicy(vehicle_policies=[])
    l_sumo_sub_policy = colmto.cse.policy.SUMOSpeedPolicy(speed_range=(0., 60.))
    l_sumo_policy.add_vehicle_policy(l_sumo_sub_policy)

    assert_true(
        l_sumo_policy.subpolicies_apply_to(
            colmto.environment.vehicle.SUMOVehicle(
                speed_max=50.,
            )
        )
    )

    assert_true(
        l_sumo_sub_policy.applies_to(
            colmto.environment.vehicle.SUMOVehicle(
                speed_max=50.,
            )
        )
    )

    l_sumo_policy = colmto.cse.policy.SUMOExtendablePolicy(vehicle_policies=[], rule="all")
    l_sumo_policy.add_vehicle_policy(l_sumo_sub_policy)

    assert_true(
        l_sumo_policy.subpolicies_apply_to(
            colmto.environment.vehicle.SUMOVehicle(
                speed_max=50.,
            )
        )
    )

    assert_true(
        l_sumo_sub_policy.applies_to(
            colmto.environment.vehicle.SUMOVehicle(
                speed_max=50.,
            )
        )
    )


def test_sumo_universal_policy():
    """Test SUMOUniversalPolicy class"""

    with assert_raises(TypeError):
        colmto.cse.policy.SUMOUniversalPolicy().applies_to("foo")

    assert_true(
        colmto.cse.policy.SUMOUniversalPolicy().applies_to(
            colmto.environment.vehicle.SUMOVehicle()
        )
    )

    assert_equal(
        colmto.cse.policy.SUMOUniversalPolicy().apply(
            [colmto.environment.vehicle.SUMOVehicle()]
        )[0].vehicle_class,
        "custom1"
    )


def test_sumo_speed_policy():
    """
    Test SUMOSpeedPolicy class
    """
    l_sumo_policy = colmto.cse.policy.SUMOSpeedPolicy(speed_range=numpy.array((0., 60.)))
    assert_is_instance(l_sumo_policy, colmto.cse.policy.SUMOSpeedPolicy)

    l_vehicles = [
        colmto.environment.vehicle.SUMOVehicle(
            speed_max=random.randrange(0, 120)
        ) for _ in xrange(4711)
        ]

    l_results = l_sumo_policy.apply(l_vehicles)

    for i in xrange(len(l_results)):
        if 0. <= l_vehicles[i].speed_max <= 60.0:
            assert_equal(
                l_results[i].vehicle_class,
                colmto.cse.policy.SUMOPolicy.to_disallowed_class()
            )
        else:
            assert_equal(
                l_results[i].vehicle_class,
                colmto.cse.policy.SUMOPolicy.to_allowed_class()
            )

    assert_equal(
        str(
            colmto.cse.policy.SUMOSpeedPolicy(
                speed_range=(0., 60.),
                behaviour=colmto.cse.policy.BEHAVIOUR.deny
            ).add_vehicle_policy(
                colmto.cse.policy.SUMOPositionPolicy(
                    position_bbox=((0., -1.), (100., 1.))
                )
            )
        ),
        "<class 'colmto.cse.policy.SUMOSpeedPolicy'>: speed_range = [  0.  60.], behaviour = 0, "
        "subpolicies: []: <class 'colmto.cse.policy.SUMOPositionPolicy'>: "
        "position_bbox = ((0.0, -1.0), (100.0, 1.0)), behaviour = 0, subpolicies: []: "
    )


def test_sumo_position_policy():
    """
    Test SUMOPositionPolicy class
    """
    l_sumo_policy = colmto.cse.policy.SUMOPositionPolicy(position_bbox=((0., -1.), (100., 1.)))
    assert_is_instance(l_sumo_policy, colmto.cse.policy.SUMOPositionPolicy)

    l_vehicles = [
        colmto.environment.vehicle.SUMOVehicle() for _ in xrange(4711)
        ]
    for i_vehicle in l_vehicles:
        i_vehicle.position = (random.randrange(0, 200), 0.)

    l_results = l_sumo_policy.apply(l_vehicles)

    for i in xrange(len(l_results)):
        if 0. <= l_vehicles[i].position[0] <= 100.0:
            assert_true(
                l_sumo_policy.applies_to(l_vehicles[i])
            )
            assert_equal(
                l_results[i].vehicle_class,
                colmto.cse.policy.SUMOPolicy.to_disallowed_class()
            )
        else:
            assert_false(
                l_sumo_policy.applies_to(l_vehicles[i])
            )
            assert_equal(
                l_results[i].vehicle_class,
                colmto.cse.policy.SUMOPolicy.to_allowed_class()
            )

    assert_tuple_equal(
        colmto.cse.policy.SUMOPositionPolicy(
            position_bbox=((0., -1.), (100., 1.)),
            behaviour=colmto.cse.policy.BEHAVIOUR.deny
        ).position_bbox,
        ((0., -1.), (100., 1.))
    )

    assert_equal(
        str(
            colmto.cse.policy.SUMOPositionPolicy(
                position_bbox=((0., -1.), (100., 1.)),
                behaviour=colmto.cse.policy.BEHAVIOUR.deny
            ).add_vehicle_policy(
                colmto.cse.policy.SUMOSpeedPolicy(
                    speed_range=(0., 60.)
                )
            )
        ),
        "<class 'colmto.cse.policy.SUMOPositionPolicy'>: position_bbox = ((0.0, -1.0), (100.0, 1.0))"
        ", behaviour = 0, subpolicies: []: <class 'colmto.cse.policy.SUMOSpeedPolicy'>: speed_range "
        "= [  0.  60.], behaviour = 0, subpolicies: []: "
    )
