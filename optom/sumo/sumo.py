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
from __future__ import division
from __future__ import print_function

import os
from sumolib import checkBinary
from collections import defaultdict
from optom.common.io import Writer
from optom.common.statistics import Statistics
from optom.common import log
import sumocfg
from sumocfg import SumoConfig
from runtime import Runtime


class Sumo(object):

    def __init__(self, p_args):
        self._log = log.logger(__name__, p_args.loglevel, p_args.quiet, p_args.logfile)

        self._sumocfg = SumoConfig(p_args, checkBinary("netconvert"), checkBinary("duarouter"))
        self._writer = Writer(p_args)
        self._statistics = Statistics(p_args)
        self._allscenarioruns = {}  # map scenarios -> runid -> files
        self._runtime = Runtime(p_args, self._sumocfg,
                                checkBinary("sumo")
                                if self._sumocfg.get("headless")
                                else checkBinary("sumo-gui"))

    def _run_scenario(self, p_scenarioname):
        if self._sumocfg.scenarioconfig.get(p_scenarioname) is None:
            self._log.error("/!\ scenario %s not found in configuration", p_scenarioname)
            return

        # self._allscenarioruns[p_scenarioname] =
        l_scenarioruns = self._sumocfg.generate_scenario(p_scenarioname)
        l_initialsortings = self._sumocfg.runconfig.get("initialsortings")

        l_iloopresults = defaultdict(dict)
        for i_initialsorting in l_initialsortings:
            l_scenarioruns.get("runs")[i_initialsorting] = {}
            for i_run in xrange(self._sumocfg.runconfig.get("runs")):
                # l_scenarioruns.get("runs").get(i_initialsorting)[i_run] =
                l_runcfg = self._sumocfg.generate_run(
                    l_scenarioruns, i_initialsorting, i_run
                )

                self._runtime.run(l_runcfg, p_scenarioname, i_run)

                self._log.debug("Converting induction loop XMLs with etree.XSLT")

                l_iloopresults = self._statistics.traveltimes_from_iloops(
                    l_runcfg,
                    self._sumocfg.scenarioconfig.get(p_scenarioname)
                )
                if i_run % 10 == 0:
                    self._log.info(
                        "Scenario %s, sorting %s: Finished run %d/%d",
                        p_scenarioname,
                        i_initialsorting,
                        i_run+1,
                        len(l_scenarioruns.get("runs").get(i_initialsorting))
                    )
                self._log.debug("Writing {} results".format(p_scenarioname))
                self._writer.write_json_pretty(
                    dict(l_iloopresults),
                    os.path.join(self._sumocfg.resultsdir, "{}-{}-{}-TT-TL.json.gz".format(p_scenarioname, i_initialsorting, i_run))
                )

    def run_scenarios(self):
        for i_scenarioname in self._sumocfg.runconfig.get("scenarios"):
            self._run_scenario(i_scenarioname)

    def _clean_runs(self):
        pass
