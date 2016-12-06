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
optom: Test module for common.statistics.
"""
import cStringIO

from nose.tools import assert_equal
from nose.tools import assert_raises

import optom.common.io
import optom.common.statistics
import optom.environment.vehicle


def test_fcd_stats():
    """
    Test fcd_stats method
    """
    l_fcdfile = cStringIO.StringIO("""
    <fcd-export xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/fcd_file.xsd">
    <timestep time="0.00">
        <vehicle id="vehicle0" x="4.40" y="0.05" angle="90.00" type="vehicle0"
        speed="27.78" pos="4.40" lane="enter_21start_0" slope="0.00"/>
    </timestep>
    <timestep time="1.00">
        <vehicle id="vehicle0" x="30.89" y="0.05" angle="90.00" type="vehicle0"
        speed="26.49" pos="30.89" lane="enter_21start_0" slope="0.00"/>
    </timestep>
    <timestep time="2.00">
        <vehicle id="vehicle0" x="57.63" y="0.05" angle="90.00" type="vehicle0"
        speed="26.75" pos="57.63" lane="enter_21start_0" slope="0.00"/>
    </timestep>
    </fcd-export>
    """)

    l_run_data = {
        "fcdfile": l_fcdfile,
        "vehicles": {
            "vehicle0": optom.environment.vehicle.SUMOVehicle(**{"speed_max": 27.777})
        }
    }

    l_result = {
        "vehicle0": {
            "maxspeed": 27.777,
            "posx": {
                "30.89": {
                    "angle": "90.00",
                    "lane": "enter_21start_0",
                    "lanepos": "30.89",
                    "speed": "26.49",
                    "timestep": 1.0,
                    "y": "0.05"
                },
                "4.40": {
                    "angle": "90.00",
                    "lane": "enter_21start_0",
                    "lanepos": "4.40",
                    "speed": "27.78",
                    "timestep": 0.0,
                    "y": "0.05"
                },
                "57.63": {
                    "angle": "90.00",
                    "lane": "enter_21start_0",
                    "lanepos": "57.63",
                    "speed": "26.75",
                    "timestep": 2.0,
                    "y": "0.05"
                }
            },
            "timesteps": {
                "0.00": {
                    "angle": "90.00",
                    "lane": "enter_21start_0",
                    "lanepos": "4.40",
                    "speed": "27.78",
                    "x": "4.40",
                    "y": "0.05"
                },
                "1.00": {
                    "angle": "90.00",
                    "lane": "enter_21start_0",
                    "lanepos": "30.89",
                    "speed": "26.49",
                    "x": "30.89",
                    "y": "0.05"
                },
                "2.00": {
                    "angle": "90.00",
                    "lane": "enter_21start_0",
                    "lanepos": "57.63",
                    "speed": "26.75",
                    "x": "57.63",
                    "y": "0.05"
                }
            },
            "type": "vehicle0"
        }
    }

    l_statistics = optom.common.statistics.Statistics(None).fcd_stats(l_run_data)
    assert_equal(l_statistics, l_result)


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

    # test for data sets with less than 6 elements -> should raise ArithmeticError
    for i_elements in xrange(5):
        assert_raises(
            ArithmeticError,
            optom.common.statistics.Statistics.h_spread,
            xrange(i_elements)
        )
