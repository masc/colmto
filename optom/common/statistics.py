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

import numpy


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
    def aggregate_vehicle_grid_stats(vehicles):
        r"""
        Aggregates vehicle grid stats related to cells.

        Aggregate time losses in cells by using the median time loss if more than one (1) element
        got recorded, otherwise just replace the list with its containing element.

        For example
        \code{.py}
        { "time_loss": [ [1.0, 2.0, 3.0, 5.0, 7.0], [8.0], [9.0] ] ... }
        \endcode
        will result in
        \code{.py}
        { "time_loss": [ 3.0, 8.0, 9.0 ] ... }
        \endcode

        @param vehicles dictionary vID -> vObj from vehicle object
        @retval vehicles with travel_stats median aggregated
        """
        for i_vehicle in vehicles.itervalues():

            l_travel_stats = i_vehicle.travel_stats.get("grid")

            for i_idx in xrange(len(l_travel_stats.get("pos_x"))):
                l_travel_stats.get("pos_x")[i_idx] = numpy.median(
                    l_travel_stats.get("pos_x")[i_idx]
                ) if len(l_travel_stats.get("pos_x")[i_idx]) > 1 \
                    else l_travel_stats.get("pos_x")[i_idx][0]

            for i_idx in xrange(len(l_travel_stats.get("pos_y"))):
                l_travel_stats.get("pos_y")[i_idx] = numpy.median(
                    l_travel_stats.get("pos_y")[i_idx]
                ) if len(l_travel_stats.get("pos_y")[i_idx]) > 1 \
                    else l_travel_stats.get("pos_y")[i_idx][0]

            for i_idx in xrange(len(l_travel_stats.get("speed"))):
                l_travel_stats.get("speed")[i_idx] = numpy.median(
                    l_travel_stats.get("speed")[i_idx]
                ) if len(l_travel_stats.get("speed")[i_idx]) > 1 \
                    else l_travel_stats.get("speed")[i_idx][0]

            for i_idx in xrange(len(l_travel_stats.get("time_loss"))):
                l_travel_stats.get("time_loss")[i_idx] = numpy.median(
                    l_travel_stats.get("time_loss")[i_idx]
                ) if len(l_travel_stats.get("time_loss")[i_idx]) > 1 \
                    else l_travel_stats.get("time_loss")[i_idx][0]

            for i_idx in xrange(len(l_travel_stats.get("dissatisfaction"))):
                l_travel_stats.get("dissatisfaction")[i_idx] = numpy.median(
                    l_travel_stats.get("dissatisfaction")[i_idx]
                ) if len(l_travel_stats.get("dissatisfaction")[i_idx]) > 1 \
                    else l_travel_stats.get("dissatisfaction")[i_idx][0]

        return vehicles

    @staticmethod
    def fairness_of(vehicles):
        r"""
        Calculate fairness from vehicle stats.

        Returns \code{.py}{ "fairness": { "time_loss": value, "speed": value,
            "dissatisfaction": value }, "vehicles": vehicles }\endcode

        @param vehicles: dictionary of vehicle objects (vID -> Vehicle)
        @retval dictionary containing vehicles and fairness dicts
        """
        return {
            "fairness": {
                "time_loss:": Statistics.h_spread(
                    numpy.array(
                        [i_vehicle.travel_stats.get("step").get("time_loss")[-1]
                         for i_vehicle in vehicles.itervalues()]
                    )
                ),
                "speed:": Statistics.h_spread(
                    numpy.array(
                        [i_vehicle.travel_stats.get("step").get("speed")[-1]
                         for i_vehicle in vehicles.itervalues()]
                    )
                ),
                "dissatisfaction:": Statistics.h_spread(
                    numpy.array(
                        [i_vehicle.travel_stats.get("step").get("dissatisfaction")[-1]
                         for i_vehicle in vehicles.itervalues()]
                    )
                ),
            },
            "vehicles": vehicles
        }

    @staticmethod
    def stats_to_hd5matrices(vehicle_stats):
        r"""
        Join vehicle stat lists to HD5 suitable matrices.

        Join fairness of \f$\text{time_loss}\f$, \f$\text{speed}\f$ and
        \f$\text{dissatisfaction}\f$ into one row-matrix and corresponding annotations.
        Join vehicle step and grid stats into one row-matrices with corresponding annotations.

        @param vehicle_stats: vehicle stats as provided by fairness_of method
        @retval vehicle stats
        """
        return {
            "fairness": {
                "value": numpy.array(
                    [
                        v for _, v in sorted(vehicle_stats.get("fairness").iteritems())
                    ]
                ),
                "annotation": "vehicle fairness:\n  - {}".format(
                    "  - \n".join(sorted(vehicle_stats.get("fairness")))
                )
            },
            "vehicles": {
                "step": {
                    "value": numpy.array(
                        [
                            v for _, v in sorted(vehicle_stats.get("step").iteritems())
                        ]
                    ),
                    "annotation": "vehicle step:\n  - {}".format(
                        "  - \n".join(sorted(vehicle_stats.get("step")))
                    )
                },
                "grid": {
                    "value": numpy.array(
                        [
                            v for _, v in sorted(vehicle_stats.get("grid").iteritems())
                        ]
                    ),
                    "annotation": "vehicle step:\n  - {}".format(
                        "  - \n".join(sorted(vehicle_stats.get("grid")))
                    )
                }
            }
        }

    @staticmethod
    def h_spread(data):
        """
        Calculate H-Spread of Hinge for given data points.
        \f{eqnarray*}{
            \text{Hinge} &=& H_2 - H_1 \text{with} \\
            H_1 &=& a_{n+2} = a_{(N+3)/4} \\
            M &=& a_{2n+3} = a_{(N+1)/2} \\
            H_2 &=& a_{3n+4} = a_{(3N+1)/4}.
        \f}
        Using numpy.percentile (speedup) with linear (=default) interpolation.
        @see Weisstein, Eric W. H-Spread. From MathWorld--A Wolfram Web Resource.
        http://mathworld.wolfram.com/H-Spread.html
        @see Weisstein, Eric W. Hinge. From MathWorld--A Wolfram Web Resource.
        http://mathworld.wolfram.com/Hinge.html
        @param data: Iterable set of data elements of (preferably) \f$4n+5\f$ for \f$n=0,1,...,N\f$,
            i.e. minimum length is \f$5\f$
        @retval Hinge if data contains at least 5 elements,
            otherwise raises ArithmeticError
        """
        # pylint: disable=no-member
        return numpy.subtract(*numpy.percentile(data, [75, 25]))
        # pylint: enable=no-member
