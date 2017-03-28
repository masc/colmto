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
colmto: Test module for environment.vehicle.
"""
import numpy
from nose.tools import assert_equal
from nose.tools import assert_almost_equal
from nose.tools import assert_true
from nose.tools import assert_list_equal


import colmto.environment.vehicle


def test_basevehicle():
    """
    Test BaseVehicle class
    """

    # test default values
    l_basevehicle = colmto.environment.vehicle.BaseVehicle()

    assert_equal(l_basevehicle.speed, 0.0)
    assert_true(numpy.array_equal(l_basevehicle.position, numpy.array([0.0, 0])))

    # test custom values
    l_basevehicle = colmto.environment.vehicle.BaseVehicle()
    l_basevehicle.position = numpy.array([23.0, 0])
    l_basevehicle.speed = 12.1

    assert_equal(
        l_basevehicle.speed,
        12.1
    )
    assert_true(
        numpy.array_equal(l_basevehicle.position, numpy.array([23.0, 0]))
    )
    assert_true(
        numpy.array_equal(l_basevehicle.properties.get("position"), numpy.array([23.0, 0]))
    )
    assert_equal(
        l_basevehicle.properties.get("speed"),
        12.1
    )


def test_sumovehicle():
    """
    Test SUMOVehicle class.
    """

    # test default values
    l_sumovehicle = colmto.environment.vehicle.SUMOVehicle()

    assert_equal(l_sumovehicle.speed_max, 0.0)
    assert_equal(l_sumovehicle.speed, 0.0)
    assert_true(numpy.array_equal(l_sumovehicle.position, numpy.array((0.0, 0))))
    assert_equal(l_sumovehicle.vehicle_type, None)
    assert_true(numpy.array_equal(l_sumovehicle.color, numpy.array((255, 255, 0, 255))))

    # test custom values
    l_sumovehicle = colmto.environment.vehicle.SUMOVehicle(
        speed_max=27.777,
        speed_deviation=1.2,
        vehicle_type="passenger",
        vtype_sumo_cfg={
            "length": 3.00,
            "minGap": 2.50
        }
    )
    l_sumovehicle.position = numpy.array([42.0, 0])
    l_sumovehicle.color = (128, 64, 255, 255)
    l_sumovehicle.speed_current = 12.1
    l_sumovehicle.start_time = 13

    assert_equal(l_sumovehicle.speed_max, 27.777)
    assert_equal(l_sumovehicle.speed_current, 12.1)
    assert_true(numpy.array_equal(l_sumovehicle.position, numpy.array([42.0, 0])))
    assert_equal(l_sumovehicle.vehicle_type, "passenger")
    assert_true(numpy.array_equal(l_sumovehicle.color, numpy.array((128, 64, 255, 255))))
    assert_equal(l_sumovehicle.start_time, 13)
    assert_true(
        numpy.array_equal(
            l_sumovehicle.grid_position,
            numpy.array((0, 0))
        )
    )
    l_sumovehicle.grid_position = (1, 2)
    assert_true(
        numpy.array_equal(
            l_sumovehicle.grid_position,
            numpy.array((1, 2))
        )
    )
    assert_true(
        numpy.array_equal(
            l_sumovehicle.properties.get("grid_position"), numpy.array((1, 2))
        )
    )
    assert_equal(
        l_sumovehicle.travel_time,
        0.0
    )
    assert_equal(
        l_sumovehicle.travel_stats,
        {
            "start_time": 0.0,
            "travel_time": 0.0,
            "vehicle_type": l_sumovehicle.vehicle_type,
            "step": {
                "dissatisfaction": [],
                "number": [],
                "pos_x": [],
                "pos_y": [],
                "relative_time_loss": [],
                "speed": [],
                "time_loss": []
            },
            "grid": {
                "dissatisfaction": [],
                "pos_x": [],
                "pos_y": [],
                "relative_time_loss": [],
                "speed": [],
                "time_loss": []
            }
        }
    )


def test_dissatisfaction():
    """Test dissatisfaction method"""
    l_sumovehicle = colmto.environment.vehicle.SUMOVehicle()
    l_data = (
        9.079162e-05, 2.467587e-04, 6.704754e-04, 1.820444e-03, 4.933049e-03, 1.329671e-02,
        3.533684e-02, 9.055700e-02, 2.130140e-01, 4.238831e-01, 6.666667e-01, 8.446376e-01,
        9.366211e-01, 9.757111e-01, 9.909253e-01, 9.966423e-01, 9.987622e-01, 9.995443e-01,
        9.998323e-01, 9.999383e-01, 9.999773e-01, 9.999916e-01, 9.999969e-01, 9.999989e-01,
        9.999996e-01, 9.999998e-01, 9.999999e-01, 1.000000e+00, 1.000000e+00, 1.000000e+00
    )
    for i_time_loss in xrange(30):
        assert_almost_equal(
            # pylint: disable=protected-access
            l_sumovehicle._dissatisfaction(
                time_loss=i_time_loss+10,
                optimal_travel_time=100,
                time_loss_threshold=0.2
            ),
            # pylint: enable=protected-access
            l_data[i_time_loss]
        )


def test_update():
    """Test update"""
    l_sumovehicle = colmto.environment.vehicle.SUMOVehicle()
    l_sumovehicle.update(
        position=(1, 2),
        lane_index=1,
        speed=12.1
    )
    assert_true(
        numpy.array_equal(
            l_sumovehicle.position,
            numpy.array((1, 2))
        )
    )
    assert_equal(
        l_sumovehicle.speed,
        12.1
    )
    assert_true(
        numpy.array_equal(
            l_sumovehicle.grid_position,
            numpy.array((-1, 1))
        )
    )


def test_record_travel_stats():
    """Test colmto.environment.vehicle.SUMOVehicle.record_travel_stats"""
    l_sumovehicle = colmto.environment.vehicle.SUMOVehicle(
        vehicle_type="passenger",
        speed_deviation=0.0,
        speed_max=100.,
    )
    l_sumovehicle.properties["dsat_threshold"] = 0.
    l_sumovehicle.record_travel_stats(1)
    l_sumovehicle.record_travel_stats(2)
    assert_equal(
        l_sumovehicle.travel_stats.get("travel_time"),
        2.0
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("step").get("number"),
        [1, 2]
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("step").get("pos_x"),
        [0.0, 0.0]
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("step").get("pos_y"),
        [0.0, 0.0]
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("step").get("time_loss"),
        [0.0, 2.0]
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("step").get("relative_time_loss"),
        [0.0, float('inf')]
    )
    assert_almost_equal(
        l_sumovehicle.travel_stats.get("step").get("dissatisfaction")[0],
        0.0
    )
    assert_almost_equal(
        l_sumovehicle.travel_stats.get("step").get("dissatisfaction")[1],
        0.93662106166696235
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("grid").get("dissatisfaction"),
        [[0.0]]
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("grid").get("pos_x"),
        [[0, 0]]
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("grid").get("pos_y"),
        [[0, 0]]
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("grid").get("speed"),
        [[0.0, 0.0]]
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("grid").get("time_loss"),
        [[0.0]]
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("grid").get("relative_time_loss"),
        [[0.0]]
    )
    l_sumovehicle.update(position=(3., 0.), lane_index=0, speed=3.)
    l_sumovehicle.record_travel_stats(3)
    assert_list_equal(
        l_sumovehicle.travel_stats.get("grid").get("dissatisfaction")[0],
        [0.0]
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("grid").get("time_loss")[0],
        [0.0]
    )
    assert_list_equal(
        l_sumovehicle.travel_stats.get("grid").get("relative_time_loss")[0],
        [0.0]
    )
    l_sumovehicle.update(position=(6., 0.), lane_index=0, speed=3.)
    l_sumovehicle.record_travel_stats(4)
    assert_almost_equal(
        l_sumovehicle.travel_stats.get("grid").get("dissatisfaction"),
        [[0.0], [0.99036954025194568]]
    )
    assert_almost_equal(
        l_sumovehicle.travel_stats.get("grid").get("time_loss"),
        [[0.0], [3.9399999999999999]]
    )
    assert_almost_equal(
        l_sumovehicle.travel_stats.get("grid").get("relative_time_loss"),
        [[0.0], [65.666666666666671]]
    )
