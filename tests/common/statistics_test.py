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
optom: Test module for common.statistics.
"""
import optom.common.statistics
import optom.environment.vehicle
import optom.common.helper
import optom.common.io

from nose.tools import assert_equal
from nose.tools import assert_is_instance
from nose.tools import assert_not_is_instance
from nose.tools import assert_raises


def test_statistics():
    """Test statistics class."""
    assert_is_instance(
        optom.common.statistics.Statistics(None),
        optom.common.statistics.Statistics
    )
    assert_is_instance(
        optom.common.statistics.Statistics(
            optom.common.helper.Namespace(
                loglevel="debug", quiet=False, logfile="foo.log"
            )
        ),
        optom.common.statistics.Statistics
    )

    with assert_raises(AttributeError):
        optom.common.statistics.Statistics("foo")


def test_closestpositiontodetector():
    """Test closest_position_to_detector"""
    # pylint: disable=protected-access
    assert_equal(
        optom.common.statistics.Statistics._closest_position_to_detector(
            vehicle_positions=[0],
            detector_position=0
        ),
        0
    )
    assert_equal(
        optom.common.statistics.Statistics._closest_position_to_detector(
            vehicle_positions=[0, 1, 2],
            detector_position=1
        ),
        1
    )
    assert_equal(
        optom.common.statistics.Statistics._closest_position_to_detector(
            vehicle_positions=[0, 1, 2],
            detector_position=2
        ),
        2
    )
    assert_equal(
        optom.common.statistics.Statistics._closest_position_to_detector(
            vehicle_positions=[0, 1, 2, 10],
            detector_position=8
        ),
        3
    )
    assert_equal(
        optom.common.statistics.Statistics._closest_position_to_detector(
            vehicle_positions=[0, 1, 2, 10],
            detector_position=3
        ),
        2
    )
    assert_equal(
        optom.common.statistics.Statistics._closest_position_to_detector(
            vehicle_positions=[0, 1, 2, 10],
            detector_position=11
        ),
        -1
    )
    # pylint: enable=protected-access


def test_h_spread():
    """
    Test H-Spread function.

    Example data taken from http://mathworld.wolfram.com/Hinge.html
    """

    l_data = (150, 250, 688, 795, 795, 795, 895, 895, 895,
              1099, 1166, 1333, 1499, 1693, 1699, 1775, 1895)

    assert_equal(
        optom.common.statistics.Statistics.h_spread(l_data),
        704
    )

    assert_equal(
        optom.common.statistics.Statistics.h_spread(xrange(10**6)),
        499999.5
    )


def test_aggregate_hdf5():
    """Test aggregate_vehicle_grid_stats and stats_to_hdf5_structure."""
    l_statistics = optom.common.statistics.Statistics()

    l_vehicles = {
        i_vid: optom.environment.vehicle.SUMOVehicle(
            vehicle_type="passenger",
            speed_deviation=0.0,
            speed_max=100.,
        ).update(
            position=(0, 0),
            lane_index=0,
            speed=10.
        ) for i_vid in xrange(2)
    }
    l_vehicles.update(
        {
            i_vid: optom.environment.vehicle.SUMOVehicle(
                vehicle_type="truck",
                speed_deviation=0.0,
                speed_max=100.,
            ).update(
                position=(0, 0),
                lane_index=0,
                speed=10.
            ) for i_vid in xrange(2, 4)
        }
    )
    l_vehicles.update(
        {
            i_vid: optom.environment.vehicle.SUMOVehicle(
                vehicle_type="tractor",
                speed_deviation=0.0,
                speed_max=100.,
            ).update(
                position=(0, 0),
                lane_index=0,
                speed=10.
            ) for i_vid in xrange(4, 6)
        }
    )

    for i_vehicle in l_vehicles.itervalues():
        i_vehicle.properties["dsat_threshold"] = 0.0

    for i_step in xrange(1, 3):
        for i_vehicle in l_vehicles.itervalues():
            i_vehicle.record_travel_stats(i_step)
            i_vehicle.update(
                position=(i_vehicle.position[0]+10., 0),
                lane_index=0,
                speed=10.
            )

    l_statistics.aggregate_vehicle_grid_stats(l_vehicles)

    for i_vehicle in l_vehicles.itervalues():
        for i_element in i_vehicle.travel_stats.get("grid").get("pos_x"):
            assert_not_is_instance(i_element, list)
        for i_element in i_vehicle.travel_stats.get("grid").get("pos_y"):
            assert_not_is_instance(i_element, list)
        for i_element in i_vehicle.travel_stats.get("grid").get("speed"):
            assert_not_is_instance(i_element, list)
        for i_element in i_vehicle.travel_stats.get("grid").get("time_loss"):
            assert_not_is_instance(i_element, list)
        for i_element in i_vehicle.travel_stats.get("grid").get("relative_time_loss"):
            assert_not_is_instance(i_element, list)
        for i_element in i_vehicle.travel_stats.get("grid").get("dissatisfaction"):
            assert_not_is_instance(i_element, list)

    l_statistics.stats_to_hdf5_structure(
        l_vehicles,
        0,
        [0, 4, 6]
    )
