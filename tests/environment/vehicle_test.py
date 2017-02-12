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
optom: Test module for environment.vehicle.
"""
import numpy
from nose.tools import assert_equal
from nose.tools import assert_true

import optom.environment.vehicle


def test_basevehicle():
    """
    Test BaseVehicle class
    """

    # test default values
    l_basevehicle = optom.environment.vehicle.BaseVehicle()

    assert_equal(l_basevehicle.speed_max, 0.0)
    assert_equal(l_basevehicle.speed_current, 0.0)
    assert_true(numpy.array_equal(l_basevehicle.position, numpy.array([0.0, 0])))

    # test custom values
    l_basevehicle = optom.environment.vehicle.BaseVehicle(
        speed_max=27.777,
        speed_current=12.1,
        position=numpy.array([23.0, 0])
    )

    assert_equal(l_basevehicle.speed_max, 27.777)
    assert_equal(l_basevehicle.speed_current, 12.1)
    assert_true(numpy.array_equal(l_basevehicle.position, numpy.array([23.0, 0])))


def test_sumovehicle():
    """
    Test SUMOVehicle class.
    """

    # test default values
    l_sumovehicle = optom.environment.vehicle.SUMOVehicle()

    assert_equal(l_sumovehicle.speed_max, 0.0)
    assert_equal(l_sumovehicle.speed_current, 0.0)
    assert_true(numpy.array_equal(l_sumovehicle.position, numpy.array((0.0, 0))))
    assert_equal(l_sumovehicle.speed_deviation, 0.0)
    assert_equal(l_sumovehicle.vtype, None)
    assert_true(numpy.array_equal(l_sumovehicle.color, numpy.array((255, 255, 0, 255))))
    assert_equal(l_sumovehicle.start_time, 0.0)
    assert_equal(l_sumovehicle.vtype_sumo_cfg, {})

    # test custom values
    l_sumovehicle = optom.environment.vehicle.SUMOVehicle(
        speed_max=27.777,
        speed_current=12.1,
        position=numpy.array([42.0, 0]),
        speed_deviation=1.2,
        vtype="passenger",
        color=(128, 64, 255, 255),
        start_time=13,
        vtype_sumo_cfg={
            "length": 3.00,
            "minGap": 2.50
        }
    )

    assert_equal(l_sumovehicle.speed_max, 27.777)
    assert_equal(l_sumovehicle.speed_current, 12.1)
    assert_true(numpy.array_equal(l_sumovehicle.position, numpy.array([42.0, 0])))
    assert_equal(l_sumovehicle.speed_deviation, 1.2)
    assert_equal(l_sumovehicle.vtype, "passenger")
    assert_equal(l_sumovehicle.color, (128, 64, 255, 255))
    assert_equal(l_sumovehicle.start_time, 13)
    assert_equal(
        l_sumovehicle.vtype_sumo_cfg,
        {
            "length": "3.0",
            "minGap": "2.5"
        }
    )
