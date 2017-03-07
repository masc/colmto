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
from __future__ import print_function

import bisect

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
    def aggregate_run_stats_to_hdf5(run_stats, detector_positions):
        """
        Aggregates statistics of runs by applying the median.
        @param run_stats: run stats in dictionary
            { runID -> run stats provided by aggregate_vehicle_grid_stats }
        @param detector_positions:
        @retval updated run_stats dictionary with aggregated stats (key: "aggregated")
        """

        l_aggregated = {
            "global": {
                i_view: {
                    i_vtype: {
                        i_stat: {
                            "value": numpy.array(
                                [
                                    run_stats[i_run].get("global").get(i_view).get(i_vtype)
                                    .get(i_stat).get("value") for i_run in run_stats
                                ]
                            ),
                            "attr": {
                                "description": "global stats of {} of {} {} for each run".format(
                                    i_view, i_vtype, i_stat
                                ),
                                "rows": "runs",
                                "columns": "{} of {} {}".format(i_view, i_vtype, i_stat)
                            }
                        } for i_stat in [
                            "dissatisfaction_start",
                            "dissatisfaction_end",
                            "dissatisfaction_delta",
                            "time_loss_start",
                            "time_loss_end",
                            "time_loss_delta",
                            "relative_time_loss_start",
                            "relative_time_loss_end",
                            "relative_time_loss_delta"
                        ]
                    } for i_vtype in ["alltypes", "passenger", "truck", "tractor"]
                } for i_view in ["fairness", "driver"]
            },
            "intervals": {
                "{}-{}".format(*i_interval): {
                    i_view: {
                        i_vtype: {
                            i_stat: {
                                "value": numpy.array(
                                    [
                                        run_stats[i_run].get("intervals")
                                        .get("{}-{}".format(*i_interval)).get(i_view).get(i_vtype)
                                        .get(i_stat).get("value") for i_run in run_stats
                                    ]
                                ),
                                "attr": {
                                    "description": "interval [{}, {}] {}".format(
                                        i_interval[0],
                                        i_interval[1],
                                        "stats of {} of {} {} for each run".format(
                                            i_view, i_vtype, i_stat
                                        ),
                                    ),
                                    "rows": "runs",
                                    "columns": "{} of {} {}".format(i_view, i_vtype, i_stat)
                                }
                            } for i_stat in [
                                "dissatisfaction_start",
                                "dissatisfaction_end",
                                "dissatisfaction_delta",
                                "time_loss_start",
                                "time_loss_end",
                                "time_loss_delta",
                                "relative_time_loss_start",
                                "relative_time_loss_end",
                                "relative_time_loss_delta"
                            ]
                        } for i_vtype in ["alltypes", "passenger", "truck", "tractor"]
                    } for i_view in ["fairness", "driver"]
                } for i_interval in zip(detector_positions[:-1], detector_positions[1:])
            }
        }

        return l_aggregated

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

            for i_idx in xrange(len(l_travel_stats.get("relative_time_loss"))):
                l_travel_stats.get("relative_time_loss")[i_idx] = numpy.median(
                    l_travel_stats.get("relative_time_loss")[i_idx]
                ) if len(l_travel_stats.get("relative_time_loss")[i_idx]) > 1 \
                    else l_travel_stats.get("relative_time_loss")[i_idx][0]

            for i_idx in xrange(len(l_travel_stats.get("dissatisfaction"))):
                l_travel_stats.get("dissatisfaction")[i_idx] = numpy.median(
                    l_travel_stats.get("dissatisfaction")[i_idx]
                ) if len(l_travel_stats.get("dissatisfaction")[i_idx]) > 1 \
                    else l_travel_stats.get("dissatisfaction")[i_idx][0]

        return vehicles

    @staticmethod
    def stats_to_hdf5_structure(vehicles, run_number, detector_positions):
        r"""
        Calculates fairness, join vehicle stat lists to HD5 suitable matrices and write to provided
        hdf5 file.

        Joins fairness of time loss and dissatisfaction into one row-matrix and
        corresponding annotations.
        Join vehicle step and grid stats into one row-matrices with corresponding annotations.
        Returns \code{.py}{ "fairness": { "time_loss": value, "dissatisfaction": value },
        "vehicles": vehicles }\endcode
        @param vehicles: dictionary of vehicle objects (vID -> Vehicle)
        @param run_number: number of current run
        @param detector_positions: list of detector positions
        @retval dictionary containing vehicles and fairness dicts
        """

        l_hdf5structure = {
            "global": {
                "driver": {},
                "fairness": {}
            },
            "intervals": {}
        }

        # ### GLOBAL STATS ### #
        for i_vtype in ["alltypes", "passenger", "truck", "tractor"]:
            l_hdf5structure.get("global").get("fairness")[i_vtype] = {}
            l_hdf5structure.get("global").get("driver")[i_vtype] = {}

            for i_stat in ["dissatisfaction", "time_loss", "relative_time_loss"]:

                l_hdf5structure.get("global").get("fairness").get(i_vtype)[
                    "{}_delta".format(i_stat)
                ] = {
                    "value": numpy.array(
                        [
                            Statistics.h_spread(
                                numpy.array(
                                    [
                                        # pylint: disable=no-member
                                        numpy.subtract(
                                            *numpy.array(
                                                i_vehicle.travel_stats.get("grid")
                                                .get(i_stat)
                                            )[[-1, 0]]
                                        )
                                        # pylint: enable=no-member
                                        for i_vehicle in [
                                            v for v in vehicles.itervalues()
                                            if i_vtype in ["alltypes", v.vehicle_type]
                                        ]
                                    ]
                                )
                            )
                        ]
                    ),
                    "attr": {
                        "description": "{} {} {} vehicles\n{}\n{}\n{}".format(
                            "trend of total fairness of run {} for".format(run_number),
                            i_vtype,
                            "(delta between last and fist cell of roadway)",
                            "calculated by using the H-Spread, i.e. interquartile distance",
                            "rows:",
                            "  - 0: {}".format(i_stat),
                        ),
                        "0": i_stat,
                    }
                }

                l_hdf5structure.get("global").get("fairness").get(i_vtype)[
                    "{}_start".format(i_stat)
                ] = {
                    "value": numpy.array(
                        [
                            Statistics.h_spread(
                                numpy.array(
                                    [
                                        i_vehicle.travel_stats.get("grid")
                                        .get(i_stat)[0]
                                        for i_vehicle in [
                                            v for v in vehicles.itervalues()
                                            if i_vtype in ["alltypes", v.vehicle_type]
                                        ]
                                    ]
                                )
                            )
                        ]
                    ),
                    "attr": {
                        "description": "{} {} vehicles\n{}\n{}\n{}".format(
                            "fairness of run {} at position {} for".format(
                                run_number,
                                0
                            ),
                            i_vtype,
                            "calculated by using the H-Spread, i.e. interquartile distance",
                            "rows:",
                            "  - 0: {}".format(i_stat),
                        ),
                        "0": i_stat,
                    }
                }

                l_hdf5structure.get("global").get("fairness").get(i_vtype)[
                    "{}_end".format(i_stat)
                ] = {
                    "value": numpy.array(
                        [
                            Statistics.h_spread(
                                numpy.array(
                                    [
                                        i_vehicle.travel_stats.get("grid")
                                        .get(i_stat)[-1]
                                        for i_vehicle in [
                                            v for v in vehicles.itervalues()
                                            if i_vtype in ["alltypes", v.vehicle_type]
                                        ]
                                    ]
                                )
                            )
                        ]
                    ),
                    "attr": {
                        "description": "{} {} vehicles\n{}\n{}\n{}".format(
                            "fairness of run {} at position {} for".format(
                                run_number,
                                len(vehicles.values()[0].travel_stats.get("grid").get(i_stat))-1
                            ),
                            i_vtype,
                            "calculated by using the H-Spread, i.e. interquartile distance",
                            "rows:",
                            "  - 0: {}".format(i_stat),
                        ),
                        "0": i_stat,
                    }
                }

                l_hdf5structure.get("global").get("driver").get(i_vtype)[
                    "{}_delta".format(i_stat)
                ] = {
                    "value": numpy.array(
                        [
                            # pylint: disable=no-member
                            numpy.subtract(
                                *numpy.array(
                                    i_vehicle.travel_stats.get("grid")
                                    .get(i_stat)
                                )[[-1, 0]]
                            )
                            # pylint: enable=no-member
                            for i_vehicle in [
                                v for v in vehicles.itervalues()
                                if i_vtype in ["alltypes", v.vehicle_type]
                            ]
                        ]
                    ),
                    "attr": {
                        "description":
                            "trend of total driver {} stats of run {} for {} {} {}".format(
                                i_stat,
                                "(delta between last and fist cell of roadway)",
                                run_number,
                                i_vtype,
                                "vehicles\n{}\n{} {}".format(
                                    "rows:",
                                    "  - 0:",
                                    i_stat
                                )
                            ),
                        "0": i_stat
                    }
                }

                l_hdf5structure.get("global").get("driver").get(i_vtype)[
                    "{}_start".format(i_stat)
                ] = {
                    "value": numpy.array(
                        [
                            i_vehicle.travel_stats.get("grid").get(i_stat)[0]
                            for i_vehicle in [
                                v for v in vehicles.itervalues()
                                if i_vtype in ["alltypes", v.vehicle_type]
                            ]
                        ]
                    ),
                    "attr": {
                        "description":
                            "driver {} stats of run {} for {} {} {}".format(
                                i_stat,
                                "(from first cell of roadway)",
                                run_number,
                                i_vtype,
                                "vehicles\n{}\n{} {}".format(
                                    "rows:",
                                    "  - 0:",
                                    i_stat
                                )
                            ),
                        "0": i_stat
                    }
                }

                l_hdf5structure.get("global").get("driver").get(i_vtype)[
                    "{}_end".format(i_stat)
                ] = {
                    "value": numpy.array(
                        [
                            i_vehicle.travel_stats.get("grid").get(i_stat)[-1]
                            for i_vehicle in [
                                v for v in vehicles.itervalues()
                                if i_vtype in ["alltypes", v.vehicle_type]
                                ]
                            ]
                    ),
                    "attr": {
                        "description":
                            "driver {} stats of run {} for {} {} {}".format(
                                i_stat,
                                "(from last cell of roadway)",
                                run_number,
                                i_vtype,
                                "vehicles\n{}\n{} {}".format(
                                    "rows:",
                                    "  - 0:",
                                    i_stat
                                )
                            ),
                        "0": i_stat
                    }
                }

        # ### INTERVAL STATS ### #
        for i_interval in zip(detector_positions[:-1], detector_positions[1:]):
            l_hdf5structure.get("intervals")["{}-{}".format(*i_interval)] = {
                "fairness": {},
                "driver": {}
            }

            for i_vtype in ["alltypes", "passenger", "truck", "tractor"]:

                l_hdf5structure.get("intervals").get("{}-{}".format(*i_interval)).get("fairness")[
                    i_vtype] = {}
                l_hdf5structure.get("intervals").get("{}-{}".format(*i_interval)).get("driver")[
                    i_vtype] = {}

                for i_stat in ["dissatisfaction", "time_loss", "relative_time_loss"]:

                    l_hdf5structure.get("intervals").get("{}-{}".format(*i_interval)).get(
                        "fairness"
                    ).get(i_vtype)["{}_delta".format(i_stat)] = {
                        "value": numpy.array(
                            [
                                Statistics.h_spread(
                                    numpy.array(
                                        [
                                            # pylint: disable=no-member
                                            numpy.subtract(
                                                *numpy.array(
                                                    i_vehicle.travel_stats.get("grid")
                                                    .get(i_stat)
                                                )[[
                                                    Statistics
                                                    ._closest_position_to_detector(
                                                        i_vehicle.travel_stats.get("grid")
                                                        .get("pos_x"),
                                                        i_interval[1]
                                                    ),
                                                    Statistics
                                                    ._closest_position_to_detector(
                                                        i_vehicle.travel_stats.get("grid")
                                                        .get("pos_x"),
                                                        i_interval[0]
                                                    )
                                                ]]
                                            )
                                            # pylint: enable=no-member
                                            for i_vehicle in [
                                                v for v in vehicles.itervalues()
                                                if i_vtype in ["alltypes", v.vehicle_type]
                                            ]
                                        ]
                                    )
                                )
                            ]
                        ),
                        "attr": {
                            "description": "{} {} {} vehicles\n{}\n{}\n{}".format(
                                "trend of total fairness of run {} for".format(run_number),
                                i_vtype,
                                "(delta between last and fist cell of roadway)",
                                "calculated by using the H-Spread, i.e. interquartile distance",
                                "rows:",
                                "  - 0: {}".format(i_stat),
                            ),
                            "0": i_stat,
                        }
                    }

                    l_hdf5structure.get("intervals").get("{}-{}".format(*i_interval)).get(
                        "fairness"
                    ).get(i_vtype)["{}_start".format(i_stat)] = {
                        "value": numpy.array(
                            [
                                Statistics.h_spread(
                                    numpy.array(
                                        [
                                            i_vehicle.travel_stats.get("grid")
                                            .get(i_stat)[
                                                Statistics._closest_position_to_detector(
                                                    i_vehicle.travel_stats.get("grid")
                                                    .get("pos_x"),
                                                    i_interval[0]
                                                )
                                            ]
                                            for i_vehicle in [
                                                v for v in vehicles.itervalues()
                                                if i_vtype in ["alltypes", v.vehicle_type]
                                            ]
                                        ]
                                    )
                                )
                            ]
                        ),
                        "attr": {
                            "description": "{} {} {} vehicles\n{}\n{}\n{}".format(
                                "fairness of run {} for".format(run_number),
                                i_vtype,
                                "(at starting cell of interval)",
                                "calculated by using the H-Spread, i.e. interquartile distance",
                                "rows:",
                                "  - 0: {}".format(i_stat),
                            ),
                            "0": i_stat,
                        }
                    }

                    l_hdf5structure.get("intervals").get("{}-{}".format(*i_interval)).get(
                        "fairness"
                    ).get(i_vtype)["{}_end".format(i_stat)] = {
                        "value": numpy.array(
                            [
                                Statistics.h_spread(
                                    numpy.array(
                                        [
                                            i_vehicle.travel_stats.get("grid")
                                            .get(i_stat)[
                                                Statistics._closest_position_to_detector(
                                                    i_vehicle.travel_stats.get("grid")
                                                    .get("pos_x"),
                                                    i_interval[1]
                                                )
                                            ]
                                            for i_vehicle in [
                                                v for v in vehicles.itervalues()
                                                if i_vtype in ["alltypes", v.vehicle_type]
                                            ]
                                        ]
                                    )
                                )
                            ]
                        ),
                        "attr": {
                            "description": "{} {} {} vehicles\n{}\n{}\n{}".format(
                                "fairness of run {} for".format(run_number),
                                i_vtype,
                                "(at starting cell of interval)",
                                "calculated by using the H-Spread, i.e. interquartile distance",
                                "rows:",
                                "  - 0: {}".format(i_stat),
                            ),
                            "0": i_stat,
                        }
                    }

                    l_hdf5structure.get("intervals").get("{}-{}".format(*i_interval)).get(
                        "driver"
                    ).get(i_vtype)["{}_delta".format(i_stat)] = {
                        "value": numpy.array(
                            [
                                # pylint: disable=no-member
                                numpy.subtract(
                                    *numpy.array(
                                        i_vehicle.travel_stats.get("grid")
                                        .get(i_stat)
                                    )[[
                                        Statistics._closest_position_to_detector(
                                            i_vehicle.travel_stats.get("grid")
                                            .get("pos_x"),
                                            i_interval[1]
                                        ),
                                        Statistics._closest_position_to_detector(
                                            i_vehicle.travel_stats.get("grid")
                                            .get("pos_x"),
                                            i_interval[0]
                                        )
                                    ]]
                                )
                                # pylint: enable=no-member
                                for i_vehicle in [
                                    v for _, v in sorted(vehicles.items())
                                    if i_vtype in ["alltypes", v.vehicle_type]
                                ]
                            ]
                        ),
                        "attr": {
                            "description":
                                "Driver stats on interval "
                                "[{}, {}] of run {} for {} vehicles\nrows:\n{}".format(
                                    i_interval[0],
                                    i_interval[1],
                                    run_number,
                                    i_vtype,
                                    "  - 0: {}".format(i_stat),
                                ),
                            "0": i_stat,
                        }
                    }

                    l_hdf5structure.get("intervals").get("{}-{}".format(*i_interval)).get(
                        "driver"
                    ).get(i_vtype)["{}_start".format(i_stat)] = {
                        "value": numpy.array(
                            [
                                i_vehicle.travel_stats.get("grid").get(i_stat)[
                                    Statistics._closest_position_to_detector(
                                        i_vehicle.travel_stats.get("grid")
                                        .get("pos_x"),
                                        i_interval[0]
                                    )
                                ]
                                for i_vehicle in [
                                    v for _, v in sorted(vehicles.items())
                                    if i_vtype in ["alltypes", v.vehicle_type]
                                ]
                            ]
                        ),
                        "attr": {
                            "description":
                                "Driver stats on interval "
                                "[{}, {}] of run {} for {} vehicles\nrows:\n{}".format(
                                    i_interval[0],
                                    i_interval[1],
                                    run_number,
                                    i_vtype,
                                    "  - 0: {}".format(i_stat),
                                ),
                            "0": i_stat,
                        }
                    }

                    l_hdf5structure.get("intervals").get("{}-{}".format(*i_interval)).get(
                        "driver"
                    ).get(i_vtype)["{}_end".format(i_stat)] = {
                        "value": numpy.array(
                            [
                                i_vehicle.travel_stats.get("grid").get(i_stat)[
                                    Statistics._closest_position_to_detector(
                                        i_vehicle.travel_stats.get("grid")
                                        .get("pos_x"),
                                        i_interval[1]
                                    )
                                ]
                                for i_vehicle in [
                                    v for _, v in sorted(vehicles.items())
                                    if i_vtype in ["alltypes", v.vehicle_type]
                                ]
                            ]
                        ),
                        "attr": {
                            "description":
                                "Driver stats on interval "
                                "[{}, {}] of run {} for {} vehicles\nrows:\n{}".format(
                                    i_interval[0],
                                    i_interval[1],
                                    run_number,
                                    i_vtype,
                                    "  - 0: {}".format(i_stat),
                                ),
                            "0": i_stat,
                        }
                    }

        l_hdf5structure["step-based"] = {
            i_vehicle_id: {
                "value": numpy.array(
                    [
                        i_vehicle.travel_stats.get("step").get("pos_x"),
                        i_vehicle.travel_stats.get("step").get("pos_y"),
                        i_vehicle.travel_stats.get("step").get("dissatisfaction"),
                        i_vehicle.travel_stats.get("step").get("speed"),
                        i_vehicle.travel_stats.get("step").get("time_loss"),
                        i_vehicle.travel_stats.get("step").get("relative_time_loss")

                    ]
                ),
                "attr": {
                    "description": "vehicle travel stats for run {}".format(
                        "{} of this vehicle's time step {}".format(
                            run_number,
                            "[0 ... travel time in time steps]"
                        )
                    ),
                    "rows": "- 0: pos x\n- 1: pos y\n- 2: dissatisfaction\n"
                            "- 3: speed\n- 4: time loss",
                    "columns": "time step of vehicle",
                }
            } for i_vehicle_id, i_vehicle in sorted(vehicles.iteritems())
        }

        l_hdf5structure["grid-based"] = {
            i_vehicle_id: {
                "value": numpy.array(
                    [
                        i_vehicle.travel_stats.get("grid").get("pos_x"),
                        i_vehicle.travel_stats.get("grid").get("pos_y"),
                        i_vehicle.travel_stats.get("grid").get("dissatisfaction"),
                        i_vehicle.travel_stats.get("grid").get("speed"),
                        i_vehicle.travel_stats.get("grid").get("time_loss"),
                        i_vehicle.travel_stats.get("grid").get("relative_time_loss")
                    ]
                ),
                "attr": {
                    "description": "vehicle stats of run {} for each grid cell {} ".format(
                        run_number,
                        "(see 'pos x' and 'pos y')"
                    ),
                    "rows": "- 0: pos x\n- 1: pos y\n- 2: dissatisfaction\n"
                            "- 3: speed\n- 4: time loss",
                    "columns": "travelled cells during route in step increments",
                }
            } for i_vehicle_id, i_vehicle in sorted(vehicles.iteritems())
        }

        l_hdf5structure["vehicle-stats"] = {
            i_vehicle_id: {
                "start_time": {
                    "value": i_vehicle.travel_stats.get("start_time"),
                    "attr": "{}'s start time".format(i_vehicle_id)
                },
                "travel_time": {
                    "value": i_vehicle.travel_stats.get("travel_time"),
                    "attr": "{}'s travel time".format(i_vehicle_id)
                },
                "vehicle_type": {
                    "value": i_vehicle.travel_stats.get("vehicle_type"),
                    "attr": "{}'s vehicle type".format(i_vehicle_id)
                }
            } for i_vehicle_id, i_vehicle in sorted(vehicles.iteritems())
        }

        del vehicles

        return l_hdf5structure

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

    @staticmethod
    def _closest_position_to_detector(vehicle_positions, detector_position):
        """
        Find the index of the closest vehicle position measurement
        to the given detector position (x-axis).

        By using bisect.bisect_left we can get this in O(log n) time due to the sorted nature of
        vehicle position measurements in x direction.
        @see http://stackoverflow.com/questions/12141150/
        from-list-of-integers-get-number-closest-to-a-given-value#12141511
        @param vehicle_positions: sorted list of vehicle positions in x direction
        @param detector_position: detector position
        @retval index of vehicle_positions
        """

        l_index = bisect.bisect_left(vehicle_positions, detector_position)

        if l_index == 0:
            return 0

        if l_index == len(vehicle_positions):
            # return index -1 (refs last element)
            return -1

        if vehicle_positions[l_index] - detector_position \
                < detector_position - vehicle_positions[l_index-1]:
            return l_index
        else:
            return l_index-1
