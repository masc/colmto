# -*- coding: utf-8 -*-
# @package s
# @cond LICENSE
# ######################################################################################
# # LGPL License                                                                       #
# #                                                                                    #
# # This file is part of the Optimisation of Overtaking Manoeuvres (OPTOM) project.                     #
# # Copyright (c) 2016, Malte Aschermann (malte.aschermann@tu-clausthal.de)            #
# # This program is free software: you can redistribute it and/or modify               #
# # it under the terms of the GNU Lesser General Public License as                     #
# # published by the Free Software Foundation, either version 3 of the                 #
# # License, or (at your option) any later version.                                    #
# #                                                                                    #
# # This program is distributed in the hope that it will be useful,                    #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of                     #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                      #
# # GNU Lesser General Public License for more details.                                #
# #                                                                                    #
# # You should have received a copy of the GNU Lesser General Public License           #
# # along with this program. If not, see http://www.gnu.org/licenses/                  #
# ######################################################################################
# @endcond
from __future__ import division
from __future__ import print_function

import os
from sumolib import checkBinary
from optom.common.io import Writer
from optom.common.io import Reader
from optom.common.statistics import Statistics
from optom.common import visualisation
from optom.common import log
import sumocfg
from sumocfg import SumoConfig
from runtime import Runtime


class Sumo(object):

    def __init__(self, p_args):
        self._log = log.logger(__name__, p_args.loglevel, p_args.logfile)

        self._sumocfg = SumoConfig(p_args, checkBinary("netconvert"), checkBinary("duarouter"))
        self._writer = Writer(p_args)
        self._statistics = Statistics(p_args)
        self._allscenarioruns = {} # map scenarios -> runid -> files
        self._runtime = Runtime(p_args, self._sumocfg,
                                checkBinary("sumo")
                                if self._sumocfg.get("headless")
                                else checkBinary("sumo-gui"))

    def _runScenario(self, p_scenarioname):
        if self._sumocfg.scenarioconfig.get(p_scenarioname) is None:
            self._log.error("/!\ scenario %s not found in configuration", p_scenarioname)
            return

        self._allscenarioruns[p_scenarioname] = l_scenarioruns = self._sumocfg.generateScenario(p_scenarioname)
        l_initialsortings = self._sumocfg.runconfig.get("initialsortings")

        l_iloopresults = {}

        for i_initialsorting in l_initialsortings:
            l_iloopresults[i_initialsorting] = {}
            l_scenarioruns.get("runs")[i_initialsorting] = {}
            for i_run in xrange(self._sumocfg.runconfig.get("runs")):
                l_scenarioruns.get("runs").get(i_initialsorting)[i_run] = l_runcfg = self._sumocfg.generateRun(l_scenarioruns, i_initialsorting, i_run)
                self._runtime.run(l_runcfg, p_scenarioname, i_run)
                self._log.debug("Converting induction loop XMLs with etree.XSLT")
                l_iloopresults.get(i_initialsorting)[i_run] = self._sumocfg.aggregate_iloop_files(l_runcfg.get("inductionloopfiles"))
                self._log.info("Finished run %d", i_run)

        self._writer.writeYAML(
            l_iloopresults,
            os.path.join(self._sumocfg.resultsdir, "iloops-{}.yaml.gz".format(p_scenarioname))
        )
        # do statistics
        #l_stats = self._statistics.compute_sumo_results(p_scenarioname, l_scenarioruns, l_iloopresults)

        # dump scenario run cfg to yaml.gz file
        self._writer.writeYAML(l_scenarioruns, os.path.join(self._sumocfg.runsdir, "runs-{}.yaml.gz".format(p_scenarioname)))
        # dump statistic results to yaml.gz/json.gz file
        #self._writer.writeYAML(l_stats, os.path.join(self._sumocfg.resultsdir, "results-{}.yaml.gz".format(p_scenarioname)))

        l_vtypedistribution = self._sumocfg.runconfig.get("vtypedistribution")
        l_vtypedistribution = ", ".join(["{}: ${}$".format(vtype, l_vtypedistribution.get(vtype).get("fraction")) for vtype in l_vtypedistribution])
        l_ttscenarioname = "".join(["\\texttt{",p_scenarioname,"}"])

        # visualisation.boxplot(os.path.join(self._sumocfg.resultsdir, "Traveltime-{}_{}_vehicles_{}runs_one21segment.{}".format(p_scenarioname, l_stats.get("nbvehicles"), l_stats.get("nbruns"), "pdf")),
        #                       l_stats.get("data").get("duration"),
        #                       "{}:\nTravel time for ${}$ vehicles, ${}$ runs for each mode ({}),\none 2+1 segment, vtype distribution: {}".format(l_ttscenarioname, l_stats.get("nbvehicles"), l_stats.get("nbruns"), ", ".join(l_initialsortings), l_vtypedistribution),
        #                       "initial ordering of vehicles (maximum speed)",
        #                       "travel time in seconds"
        #                       )
        #
        # visualisation.boxplot(os.path.join(self._sumocfg.resultsdir, "TimeLoss-{}_{}_vehicles_{}runs_one21segment.{}".format(p_scenarioname, l_stats.get("nbvehicles"), l_stats.get("nbruns"), "pdf")),
        #                       l_stats.get("data").get("timeLoss"),
        #                       "{}:\nTime loss for ${}$ vehicles, ${}$ runs for each mode ({}),\none 2+1 segment, vtype distribution: {}".format(l_ttscenarioname, l_stats.get("nbvehicles"), l_stats.get("nbruns"), ", ".join(l_initialsortings), l_vtypedistribution),
        #                       "initial ordering of vehicles (maximum speed)",
        #                       "time loss in seconds"
        #                       )
        #
        # visualisation.boxplot(os.path.join(self._sumocfg.resultsdir, "RelativeTimeLoss-{}_{}_vehicles_{}runs_one21segment.{}".format(p_scenarioname, l_stats.get("nbvehicles"), l_stats.get("nbruns"), "pdf")),
        #                       l_stats.get("data").get("relativeLoss"),
        #                       "{}:\nRelative time loss for ${}$ vehicles, ${}$ runs for each mode ({}),\none 2+1 segment, vtype distribution: {}".format(l_ttscenarioname, l_stats.get("nbvehicles"), l_stats.get("nbruns"), ", ".join(l_initialsortings), l_vtypedistribution),
        #                       "initial ordering of vehicles (maximum speed)",
        #                       "relative time loss in percent ($\\frac{\\mathrm{Traveltime}}{\\mathrm{Traveltime}-\\mathrm{Timeloss}}*100$)"
        #                       )

    def runScenarios(self):
        for i_scenarioname in self._sumocfg.runconfig.get("scenarios"):
            self._runScenario(i_scenarioname)

    def _cleanRuns(self):
        pass


