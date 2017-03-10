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

from nose.tools import assert_equal
from nose.tools import assert_is_instance
from nose.tools import assert_raises


def test_statistics():
    """Test statistics class"""

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
