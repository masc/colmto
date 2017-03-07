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
import h5py
import numpy as np
import os

f_hdf5 = h5py.File("Scenarios_baseline_time_loss.hdf5", "a")

for i_scenario in ["NI-B210", "HE-B62", "NW-B1", "HE-B49", "BY-B20", "BY-B471"]:
    for i_stat in ["dissatisfaction", "relative_time_loss", "time_loss"]:
        for i_type in ["alltypes", "passenger", "tractor", "truck"]:
            f_hdf5.create_dataset(
                name=os.path.join(
                    i_scenario,
                    "8640",
                    "best",
                    "global",
                    "driver",
                    i_type,
                    "baseline_{}".format(i_stat)
                ),
                data=np.array(
                    [
                        np.median(
                            np.array(
                                f_hdf5.get(i_scenario).get("8640").get("best").get("global")
                                .get("driver").get(i_type).get("{}_end".format(i_stat))
                            ).T[i]
                        )
                        for i in xrange(len(f_hdf5.get(i_scenario).get("8640").get("best")
                                            .get("global").get("driver").get(i_type)
                                            .get("{}_end".format(i_stat))[0]))]),
                compression="gzip",
                compression_opts=9,
                fletcher32=True,
                chunks=True
            )

f_hdf5.close()
