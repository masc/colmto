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

import os
import numpy
import pprint


class Statistics(object):
    """Statistics class for computing/aggregating SUMO results"""

    def __init__(self, args):
        if args is not None:
            self._log = optom.common.log.logger(__name__, args.loglevel, args.quiet, args.logfile)
            self._writer = optom.common.io.Writer(args)
        else:
            self._log = optom.common.log.logger(__name__)
            self._writer = optom.common.io.Writer(None)

    def aggregate_run_stats_to_hdf5(self, run_stats, hdf5_path="",  hdf5_file=None):
        """
        Aggregates statistics of runs into boxplot compatible data: 0.25 quartile, median, 0.75 quartile
        @param run_stats: run stats in dictionary { runID -> run stats provided by aggregate_vehicle_grid_stats }
        @param hdf5_path: path to put stats of this run
        @param hdf5_file: hdf5 file to write
        @retval dictionary containing aggregated stats
        """

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

    def stats_to_hdf5(self, vehicles, hdf5_path="",  hdf5_file=None):
        r"""
        Calculates fairness, join vehicle stat lists to HD5 suitable matrices and write to provided hdf5 file.

        Joins fairness of time loss, speed and dissatisfaction into one row-matrix and
        corresponding annotations.
        Join vehicle step and grid stats into one row-matrices with corresponding annotations.
        Returns \code{.py}{ "fairness": { "time_loss": value, "speed": value,
            "dissatisfaction": value }, "vehicles": vehicles }\endcode
        @param vehicles: dictionary of vehicle objects (vID -> Vehicle)
        @param hdf5_path: path to put stats of this run
        @param hdf5_file: hdf5 file to write
        @retval dictionary containing vehicles and fairness dicts
        """

        l_fairness = {
            "fairness": {
                "value": numpy.array(
                    [
                        Statistics.h_spread(
                            numpy.array(
                                [i_vehicle.travel_stats.get("step").get("dissatisfaction")[-1]
                                 for i_vehicle in vehicles.itervalues()]
                            )
                        ),
                        Statistics.h_spread(
                            numpy.array(
                                [i_vehicle.travel_stats.get("step").get("speed")[-1]
                                 for i_vehicle in vehicles.itervalues()]
                            )
                        ),
                        Statistics.h_spread(
                            numpy.array(
                                [i_vehicle.travel_stats.get("step").get("time_loss")[-1]
                                 for i_vehicle in vehicles.itervalues()]
                            )
                        )
                    ]
                ),
                "attr": {
                    "description": "global fairness of run\n"
                                   "rows:\n  - 0: dissatisfaction\n  - 1: speed\n  - 2: time loss",
                    "0": "dissatisfaction",
                    "1": "speed",
                    "2": "time loss"
                }
            }
        }

        l_steps = {
            i_vehicle_id: {
                "value": numpy.array(
                    [
                        i_vehicle.travel_stats.get("step").get("pos_x"),
                        i_vehicle.travel_stats.get("step").get("pos_y"),
                        i_vehicle.travel_stats.get("step").get("dissatisfaction"),
                        i_vehicle.travel_stats.get("step").get("speed"),
                        i_vehicle.travel_stats.get("step").get("time_loss")
                    ]
                ),
                "attr": {
                    "description": "vehicle travel stats for this vehicle's time step counting "
                                   "[0 ... travel time in time steps]",
                    "rows": "- 0: pos x\n- 1: pos y\n- 2: dissatisfaction\n"
                            "- 3: speed\n- 4: time loss",
                    "columns": "time step of vehicle",
                }
            } for i_vehicle_id, i_vehicle in sorted(vehicles.iteritems())
        }

        l_grid = {
            i_vehicle_id: {
                "value": numpy.array(
                    [
                        i_vehicle.travel_stats.get("grid").get("pos_x"),
                        i_vehicle.travel_stats.get("grid").get("pos_y"),
                        i_vehicle.travel_stats.get("grid").get("dissatisfaction"),
                        i_vehicle.travel_stats.get("grid").get("speed"),
                        i_vehicle.travel_stats.get("grid").get("time_loss"),
                    ]
                ),
                "attr": {
                    "description": "vehicle travel stats for each grid cell (see 'pos x' and 'pos y')",
                    "rows": "- 0: pos x\n- 1: pos y\n- 2: dissatisfaction\n"
                            "- 3: speed\n- 4: time loss",
                    "columns": "travelled cells during route in step increments",
                }
            } for i_vehicle_id, i_vehicle in sorted(vehicles.iteritems())
        }

        self._writer.write_hdf5(
            hdf5_file,
            os.path.join(hdf5_path, "global"),
            l_fairness,
            compression="gzip", compression_opts=9, track_times=True, fletcher32=True
        )

        self._writer.write_hdf5(
            hdf5_file,
            os.path.join(hdf5_path, "step-based"),
            l_steps,
            compression="gzip", compression_opts=9, track_times=True, fletcher32=True
        )
        self._writer.write_hdf5(
            hdf5_file,
            os.path.join(hdf5_path, "grid-based"),
            l_grid,
            compression="gzip", compression_opts=9, track_times=True, fletcher32=True
        )

        return {
            "global": l_fairness,
            "step-based": l_steps,
            "grid-based": l_grid
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
