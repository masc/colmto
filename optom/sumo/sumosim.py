# -*- coding: utf-8 -*-
# @package optom
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
"""Main module to run/initialise SUMO scenarios."""
from __future__ import division

import os
import sys
import itertools
import random

try:
    sys.path.append(os.path.join("sumo", "sumo", "tools"))
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join("..", "..")), "tools"))
    import sumolib
except ImportError:
    raise ("please declare environment variable 'SUMO_HOME' as the root"
           "directory of your sumo installation (it should contain folders 'bin',"
           "'tools' and 'docs')")

import optom.common.io
import optom.common.statistics
import optom.common.log
import optom.cse.cse
import optom.sumo.sumocfg
import optom.sumo.runtime


class SumoSim(object):
    """Class for initialising/running SUMO scenarios."""

    def __init__(self, args):
        """C'tor."""

        self._log = optom.common.log.logger(__name__, args.loglevel, args.quiet, args.logfile)
        self._args = args
        self._sumocfg = optom.sumo.sumocfg.SumoConfig(
            args,
            sumolib.checkBinary("netconvert"),
            sumolib.checkBinary("duarouter")
        )
        self._writer = optom.common.io.Writer(args)
        self._statistics = optom.common.statistics.Statistics(args)
        self._allscenarioruns = {}  # map scenarios -> runid -> files
        self._runtime = optom.sumo.runtime.Runtime(
            args,
            self._sumocfg,
            sumolib.checkBinary("sumo")
            if self._sumocfg.sumo_run_config.get("headless")
            else sumolib.checkBinary("sumo-gui")
        )

    def run_scenario(self, scenario_name):
        """
        Run given scenario.

        @param scenario_name: Scenario name to look up in cfgs.
        """

        if self._sumocfg.scenario_config.get(scenario_name) is None:
            self._log.error(r"/!\ scenario %s not found in configuration", scenario_name)
            raise Exception

        l_scenario = self._sumocfg.generate_scenario(scenario_name)
        l_vtype_list = self._sumocfg.run_config.get("vtype_list")

        if scenario_name not in l_vtype_list:
            self._log.debug("Generating new vtype_list")

            l_vtypedistribution = list(
                itertools.chain.from_iterable(
                    [
                        [k] * int(round(100 * v.get("fraction")))
                        for (k, v) in self._sumocfg.run_config.get("vtypedistribution").iteritems()
                    ]
                )
            )
            l_timebegin, l_timeend = self._sumocfg.run_config.get("simtimeinterval")
            l_numberofvehicles = int(
                round(
                    self._sumocfg.aadt(l_scenario) / (24 * 60 * 60) * (l_timeend - l_timebegin)
                )
            ) if not self._sumocfg.run_config.get("nbvehicles").get("enabled") \
                else self._sumocfg.run_config.get("nbvehicles").get("value")

            l_vtype_list[scenario_name] = [
                random.choice(l_vtypedistribution) for _ in xrange(l_numberofvehicles)
            ]
        else:
            self._log.debug("Using pre-configured vtype_list")

        for i_initial_sorting in self._sumocfg.run_config.get("initialsortings"):

            for i_run in xrange(self._sumocfg.run_config.get("runs")):

                if self._sumocfg.run_config.get("cse-enabled"):
                    # cse mode: apply cse policies to vehicles and run with TraCI
                    self._writer.write_hdf5(

                        self._statistics.stats_to_hdf5_structure(

                            self._statistics.aggregate_vehicle_grid_stats(

                                self._runtime.run_traci(
                                    self._sumocfg.generate_run(
                                        l_scenario,
                                        i_initial_sorting,
                                        i_run,
                                        l_vtype_list.get(scenario_name)
                                    ),
                                    optom.cse.cse.SumoCSE(
                                        self._args
                                    ).add_policies_from_cfg(
                                        self._sumocfg.run_config.get("policies")
                                    )
                                )
                            ),

                            run_number=i_run,

                            detector_positions=self._sumocfg.scenario_config.get(scenario_name)
                            .get("parameters").get("detectorpositions")
                        ),

                        hdf5_file=self._args.results_hdf5_file if self._args.results_hdf5_file
                        else os.path.join(self._sumocfg.resultsdir,
                                          "{}.hdf5".format(self._sumocfg.run_prefix)),
                        hdf5_base_path=os.path.join(
                            scenario_name,
                            str(self._sumocfg.aadt(self._sumocfg.generate_scenario(scenario_name))),
                            i_initial_sorting,
                            str(i_run)
                        ),
                        compression="gzip",
                        compression_opts=9,
                        fletcher32=True
                    )
                else:
                    self._runtime.run_standalone(
                        self._sumocfg.generate_run(
                            l_scenario,
                            i_initial_sorting,
                            i_run,
                            l_vtype_list.get(scenario_name)
                        )
                    )

                l_aadt = self._sumocfg.scenario_config.get(scenario_name).get(
                    "parameters"
                ).get("aadt") if not self._sumocfg.run_config.get("aadt").get("enabled") \
                    else self._sumocfg.run_config.get("aadt").get("value")
                self._log.info(
                    "Scenario %s, AADT %d (%d vph), sorting %s: Finished run %d/%d",
                    scenario_name,
                    l_aadt,
                    int(l_aadt / 24),
                    i_initial_sorting,
                    i_run + 1,
                    self._sumocfg.run_config.get("runs")
                )

    def run_scenarios(self):
        """
        Run all scenarios defined by cfgs/commandline.
        """

        for i_scenarioname in self._sumocfg.run_config.get("scenarios"):
            self.run_scenario(i_scenarioname)

        # dump configuration to run dir
        self._writer.write_yaml(
            {
                "run_config": self._sumocfg.run_config,
                "scenario_config": self._sumocfg.scenario_config,
                "vtypes_config": self._sumocfg.vtypes_config
            },
            os.path.join(self._sumocfg.sumo_config_dir, self._sumocfg.run_prefix,
                         "configuration.yaml")
        )
