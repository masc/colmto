# -*- coding: utf-8 -*-
# @package optom
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
"""Configuration super class."""
from __future__ import division
from __future__ import print_function
import numpy
import os
import sys
import h5py
import optom.common.io

def aggregate_run_stats_to_hdf5(hdf5_stats, detector_positions):
    """
    Aggregates statistics of runs by applying the median.
    @param hdf5_stats: run stats as a hdf5 object
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
                                hdf5_stats[os.path.join(
                                    i_run, "global", i_view, i_vtype, i_stat
                                )] for i_run in hdf5_stats
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
                                    hdf5_stats[os.path.join(
                                        i_run,
                                        "intervals",
                                        "{}-{}".format(*i_interval),
                                        i_view,
                                        i_vtype,
                                        i_stat
                                    )] for i_run in hdf5_stats
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


def main(argv):
    writer = optom.common.io.Writer()

    if len(argv) < 3:
        print("Usage: aggregate_runs_in_hdf5.py hdf5-input-file hdf5-output-file")
        return

    print("reading input HDF5 ({})".format(argv[1]))
    f_hdf5_input = h5py.File(argv[1], "r")
    f_hdf5_output = h5py.File(argv[2], "a", libver="latest")

    print("figuring out detector positions ...")

    l_scenarios = f_hdf5_input.keys()
    if len(l_scenarios) == 0:
        print("No scenario dirs found!")
        return

    l_aadts = f_hdf5_input[l_scenarios[0]].keys()
    if len(l_aadts) == 0:
        print("No aadt dirs found!")
        return

    l_orderings = f_hdf5_input[os.path.join(l_scenarios[0], l_aadts[0])].keys()
    if len(l_orderings) == 0:
        print("No ordering dirs found!")
        return

    l_runs = f_hdf5_input[os.path.join(l_scenarios[0], l_aadts[0], l_orderings[0])].keys()

    l_intervals = f_hdf5_input[os.path.join(
        l_scenarios[0], l_aadts[0], l_orderings[0], l_runs[0], "intervals"
    )].keys()
    l_detector_positions = sorted(
        set(
            [
                e for tupl in [
                    (int(i.split("-")[0]), int(i.split("-")[1])) for i in l_intervals
                ] for e in tupl
            ]
        )
    )
    print("... {}".format(l_detector_positions))
    print("aggregating data...")

    for i_scenario in l_scenarios:
        for i_aadt in l_aadts:
            for i_ordering in l_orderings:
                # aggregate_run_stats_to_hdf5(
                #     f_hdf5_input[os.path.join(i_scenario, i_aadt, i_ordering)],
                #     l_detector_positions
                # )
                pass

    f_hdf5_input.close()

if __name__ == "__main__":
    main(sys.argv)
