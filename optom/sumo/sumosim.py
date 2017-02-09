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
"""Main module to run/initialise SUMO scenarios."""
from __future__ import division
from __future__ import print_function

import os
import sys

try:
    sys.path.append(os.path.join("sumo", "sumo", "tools"))
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join("..", "..")), "tools"))
    import sumolib
except ImportError:
    raise ("please declare environment variable 'SUMO_HOME' as the root"
           "directory of your sumo installation (it should contain folders 'bin',"
           "'tools' and 'docs')")
import math
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

        :param scenario_name Scenario name to look up cfgs.
        """

        if self._sumocfg.scenario_config.get(scenario_name) is None:
            self._log.error(r"/!\ scenario %s not found in configuration", scenario_name)
            return

        l_scenario_runs = self._sumocfg.generate_scenario(scenario_name)
        l_initial_sortings = self._sumocfg.run_config.get("initialsortings")

        for i_initial_sorting in l_initial_sortings:
            l_scenario_runs.get("runs")[i_initial_sorting] = {}

            for i_run in xrange(self._sumocfg.run_config.get("runs")):

                l_run_config = self._sumocfg.generate_run(
                    l_scenario_runs, i_initial_sorting, i_run
                )

                if self._sumocfg.run_config.get("cse-enabled"):
                    self._runtime.run_traci(
                        l_run_config, optom.cse.cse.SumoCSE(
                            self._args
                        ).add_policies_from_cfg(
                            self._sumocfg.run_config.get("policies")
                        ).apply(
                            l_run_config.get("vehicles")
                        )
                    )
                else:
                    self._runtime.run_once(l_run_config)

                l_vehicle_data_json = self._statistics.fcd_stats(l_run_config)

                self._log.debug("Writing %s results", scenario_name)
                self._writer.write_json(
                    dict(l_vehicle_data_json),
                    os.path.join(
                        self._sumocfg.resultsdir, scenario_name, i_initial_sorting,
                        str(i_run),
                        "{}-{}-run{}-TT-TL.json.gz".format(
                            scenario_name,
                            self._sumocfg.scenario_config.get(
                                scenario_name
                            ).get("parameters").get("aadt")
                            if self._sumocfg.run_config.get("aadt").get("enabled")
                            else "{}veh".format(
                                self._sumocfg.run_config.get("nbvehicles").get("value")
                            ),
                            str(i_run).zfill(
                                int(math.ceil(math.log10(self._sumocfg.run_config.get("runs"))))
                            )
                        )
                    )
                )

                # l_csv_header = next(iter(l_vehicle_data_csv), {}).keys()
                # self._writer.write_csv(
                #     l_csv_header,
                #     l_vehicle_data_csv,
                #     os.path.join(
                #         self._sumocfg.resultsdir, p_scenario_name, i_initial_sorting,
                #         str(i_run),
                #         "{}-{}-run{}-TT-TL.csv".format(
                #             p_scenario_name,
                #             self._sumocfg.scenario_config.get(
                #                 p_scenario_name
                #             ).get("parameters").get("aadt")
                #             if self._sumocfg.run_config.get("aadt").get("enabled")
                #             else "{}veh".format(
                #                 self._sumocfg.run_config.get("nbvehicles").get("value")
                #             ),
                #             str(i_run).zfill(
                #                 int(math.ceil(math.log10(self._sumocfg.run_config.get("runs"))))
                #             )
                #         )
                #     )
                # )

                if i_run % 10 == 0:
                    self._log.info(
                        "Scenario %s, AADT %d (%d vps), sorting %s: Finished run %d/%d",
                        scenario_name,
                        self._sumocfg.run_config.get("aadt").get("value"),
                        int(self._sumocfg.run_config.get("aadt").get("value") / 24),
                        i_initial_sorting,
                        i_run + 1,
                        self._sumocfg.run_config.get("runs")
                    )

        # dump configuration
        self._writer.write_json_pretty(
            {
                "run_config": self._sumocfg.run_config,
                "scenario_config": self._sumocfg.scenario_config,
                "vtypes_config": self._sumocfg.vtypes_config
            },
            os.path.join(self._sumocfg.sumo_config_dir, self._sumocfg.run_prefix,
                         "configuration.json")
        )

    def run_scenarios(self):
        """Run all scenarios defined by cfgs/commandline."""

        for i_scenarioname in self._sumocfg.run_config.get("scenarios"):
            self.run_scenario(i_scenarioname)
