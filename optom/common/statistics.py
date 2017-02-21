# -*- coding: utf-8 -*-
# @package optom.common
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of Overtaking Manoeuvres project.   #
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
"""Statistics module"""
from __future__ import division


import optom.common.io
import optom.common.log


class Statistics(object):
    """Statistics class for computing/aggregating SUMO results"""

    def __init__(self, args):
        if args is not None:
            self._log = optom.common.log.logger(__name__, args.loglevel, args.quiet, args.logfile)
            self._writer = optom.common.io.Writer(args)
        else:
            self._log = optom.common.log.logger(__name__)
            self._writer = optom.common.io.Writer(None)

    @staticmethod
    def _aggregate_vehicle_grid_stats(travel_stats):
        """
        Aggregates vehicle stats related to cells.

        Aggregate time losses in cells by using the median time loss

        @params travel_stats: travel_stats from vehicle object
        @retval aggregated vehicle stats
        """
        # for i_item in travel_stats.get("grid_cell").itervalues():
        #     if isinstance(i_item.get("time_loss"), list):
        #         i_item["time_loss"] = numpy.median(i_item.get("time_loss"))
        #     if isinstance(i_item.get("speed"), list):
        #         i_item["speed"] = numpy.median(i_item.get("speed"))
        #     if isinstance(i_item.get("dissatisfaction"), list):
        #         i_item["dissatisfaction"] = numpy.median(i_item.get("dissatisfaction"))

        return travel_stats

    def vehicle_stats(self, vehicles):
        """

        @params vehicles:
        @retval
        """
        return [
            self._aggregate_vehicle_grid_stats(i_vobj.travel_stats)
            for i_vobj in vehicles.itervalues()
        ]

    @staticmethod
    def h_spread(data):
        """
        Calculate H-Spread of given data points.

        Weisstein, Eric W. H-Spread. From MathWorld--A Wolfram Web Resource.
        http://mathworld.wolfram.com/H-Spread.html
        Weisstein, Eric W. Hinge. From MathWorld--A Wolfram Web Resource.
        http://mathworld.wolfram.com/Hinge.html

        @param data: Iterable set of data elements of (preferably) \f$4n+5\f$ for \f$n=0,1,...,N\f$,
            i.e. minimum length is \f$5\f$

        @retval \f$H_2 - H_1\f$ if data contains at least 5 elements,
            otherwise raises ArithmeticError
        """

        l_data = sorted(data)
        l_len = len(l_data)

        if l_len < 5:
            raise ArithmeticError

        l_h1 = l_data[int((l_len + 3) / 4 - 1)]
        l_h2 = l_data[int((3 * l_len + 1) / 4 - 1)]
        return l_h2 - l_h1
