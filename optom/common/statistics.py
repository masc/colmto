# -*- coding: utf-8 -*-
# @package optom.common
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
"""Statistics module"""
from __future__ import division

from collections import defaultdict
from collections import OrderedDict

import optom.common.io
import optom.common.log


class Statistics(object):
    """Statistics class for computing/aggregating SUMO results"""

    def __init__(self, p_args):
        self._log = optom.common.log.logger(__name__, p_args.loglevel, p_args.logfile)
        self._writer = optom.common.io.Writer(p_args)

    def fcd_stats(self, p_run_data):
        """

        :param p_run_data:
        :return: json object
        """
        self._log.debug("Reading fcd file %s", p_run_data.get("fcdfile"))
        l_fcd_xml = optom.common.io.etree.parse(
            p_run_data.get("fcdfile")
        )
        l_fcd_stats_json = defaultdict(dict)

        for i_timestep in l_fcd_xml.getiterator("timestep"):

            for i_vehicle in i_timestep.getiterator("vehicle"):

                if "type" not in l_fcd_stats_json[i_vehicle.get("id")]:
                    l_fcd_stats_json[i_vehicle.get("id")]["type"] = i_vehicle.get("type")

                if "maxspeed" not in l_fcd_stats_json[i_vehicle.get("id")]:
                    l_fcd_stats_json[
                        i_vehicle.get("id")
                    ]["maxspeed"] = p_run_data.get("vehicles").get(i_vehicle.get("id")).speed_max

                if "timesteps" not in l_fcd_stats_json[i_vehicle.get("id")]:
                    l_fcd_stats_json[i_vehicle.get("id")]["timesteps"] = OrderedDict()

                l_fcd_stats_json[i_vehicle.get("id")]["timesteps"][i_timestep.get("time")] = {
                    "x": i_vehicle.get("x"),
                    "y": i_vehicle.get("y"),
                    "angle": i_vehicle.get("angle"),
                    "speed": i_vehicle.get("speed"),
                    "lane": i_vehicle.get("lane"),
                    "lanepos": i_vehicle.get("pos")
                }

                if "posx" not in l_fcd_stats_json[i_vehicle.get("id")]:
                    l_fcd_stats_json[i_vehicle.get("id")]["posx"] = OrderedDict()

                l_fcd_stats_json[i_vehicle.get("id")]["posx"][i_vehicle.get("x")] = {
                    "timestep": float(i_timestep.get("time")),
                    "y": i_vehicle.get("y"),
                    "angle": i_vehicle.get("angle"),
                    "speed": i_vehicle.get("speed"),
                    "lane": i_vehicle.get("lane"),
                    "lanepos": i_vehicle.get("pos")
                }

        # CSV
        # l_fcd_stats_csv = []
        # for i_vid in l_fcd_stats_json.iterkeys():
        #
        #     l_fcd_stats_csv_row = OrderedDict()
        #
        #     l_fcd_stats_csv_row["id"] = i_vid
        #     l_fcd_stats_csv_row["type"] = l_fcd_stats_json.get(i_vid).get("type")
        #     l_fcd_stats_csv_row["maxspeed"] = l_fcd_stats_json.get(i_vid).get("maxspeed")
        #     for i_posx, i_posx_data in l_fcd_stats_json.get(i_vid).get("posx").iteritems():
        #         l_fcd_stats_csv_row["x_{}".format(i_posx)] = i_posx_data.get("timestep")
        #
        #     l_fcd_stats_csv.append(l_fcd_stats_csv_row)

        return l_fcd_stats_json  # , l_fcd_stats_csv

    @staticmethod
    def h_spread(p_data):
        """
        Calculate H-Spread of given data points
        Weisstein, Eric W. "H-Spread." From MathWorld--A Wolfram Web Resource.
        http://mathworld.wolfram.com/H-Spread.html
        Weisstein, Eric W. "Hinge." From MathWorld--A Wolfram Web Resource.
        http://mathworld.wolfram.com/Hinge.html
        :param p_data: Iterable set of data elements of (preferably) 4n+5 for n=0,1,...,N,
                       i.e. minimum length is 5
        :return: H_2 - H_1 if p_data contains at least 5 elements, otherwise raises ArithmeticError
        """
        l_data = sorted(p_data)
        l_len = len(l_data)

        if l_len < 5:
            raise ArithmeticError

        l_h1 = l_data[int((l_len + 3) / 4 - 1)]
        l_h2 = l_data[int((3 * l_len + 1) / 4 - 1)]
        return l_h2 - l_h1
