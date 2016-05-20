# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import logging
from sumolib import checkBinary

from configuration.sumocfg import SumoConfig
from runtime.runtime import Runtime
from common.visualisation import Visualisation
from common.resultswriter import ResultsWriter
from common.statistics import Statistics

import os

class Sumo(object):

    def __init__(self, p_args):
        self._log = logging.getLogger(__name__)
        self._log.setLevel(p_args.loglevel)

        # create a file handler
        handler = logging.FileHandler(p_args.logfile)
        handler.setLevel(p_args.loglevel)

        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # add the handlers to the logger
        self._log.addHandler(handler)

        self._visualisation = Visualisation()
        self._sumocfg = SumoConfig(p_args, self._visualisation, checkBinary("netconvert"), checkBinary("duarouter"))
        self._resultswriter = ResultsWriter(p_args)
        self._statistics = Statistics(p_args)
        self._allscenarioruns = {} # map scenarios -> runid -> files
        self._runtime = Runtime(p_args, self._sumocfg, self._visualisation,
                                checkBinary("sumo")
                                if self._sumocfg.get("headless")
                                else checkBinary("sumo-gui"))


    def _runScenario(self, p_scenarioname):
        if self._sumocfg.getScenarioConfig().get(p_scenarioname) == None:
            self._log.error("/!\ scenario {} not found in configuration".format(p_scenarioname))
            return

        self._allscenarioruns[p_scenarioname] = l_scenarioruns = self._sumocfg.generateScenario(p_scenarioname)
        l_initialsortings = self._sumocfg.getRunConfig().get("initialsortings")

        for i_initialsorting in l_initialsortings:

            l_scenarioruns.get("runs")[i_initialsorting] = {}

            for i_run in xrange(self._sumocfg.getRunConfig().get("runs")):
                l_run = self._sumocfg.generateRun(l_scenarioruns, i_initialsorting, i_run)
                self._runtime.run(l_run)

        # dump scenarioruns to yaml.gz file
        self._resultswriter.writeYAML(l_scenarioruns, os.path.join(self._sumocfg.rundir, "runs-{}.yaml.gz".format(p_scenarioname)))

        # do statistics
        l_stats = self._statistics.computeSUMOResults(p_scenarioname, l_scenarioruns, p_queries=["duration","timeLoss"])

        # dump statistic results to yaml.gz file
        self._resultswriter.writeYAML(l_stats, os.path.join(self._sumocfg.rundir, "results-{}.yaml.gz".format(p_scenarioname)))
        l_vtypedistribution = self._sumocfg.getRunConfig().get("vtypedistribution")
        l_vtypedistribution = ", ".join(["{}: ${}$".format(vtype, l_vtypedistribution.get(vtype).get("fraction")) for vtype in l_vtypedistribution])
        l_ttscenarioname = "".join(["\\texttt{",p_scenarioname,"}"])
        self._visualisation.boxplot(os.path.join(self._sumocfg.rundir, "Traveltime-{}_{}_vehicles_{}runs_one21segment.{}".format(p_scenarioname, l_stats.get("nbvehicles"), l_stats.get("nbruns"), "pdf")),
                                    l_stats.get("data").get("duration"),
                                    "{}:\nTravel time for ${}$ vehicles, ${}$ runs for each mode ({}),\none 2+1 segment, vtype distribution: {}".format(l_ttscenarioname, l_stats.get("nbvehicles"), l_stats.get("nbruns"), ", ".join(l_initialsortings), l_vtypedistribution),
                                    "initial ordering of vehicles (maximum speed)",
                                    "travel time in seconds"
                                    )
        self._visualisation.boxplot(os.path.join(self._sumocfg.rundir, "TimeLoss-{}_{}_vehicles_{}runs_one21segment.{}".format(p_scenarioname, l_stats.get("nbvehicles"), l_stats.get("nbruns"), "pdf")),
                                    l_stats.get("data").get("timeLoss"),
                                    "{}:\nTime loss for ${}$ vehicles, ${}$ runs for each mode ({}),\none 2+1 segment, vtype distribution: {}".format(l_ttscenarioname, l_stats.get("nbvehicles"), l_stats.get("nbruns"), ", ".join(l_initialsortings), l_vtypedistribution),
                                    "initial ordering of vehicles (maximum speed)",
                                    "time loss in seconds"
                                    )
        self._visualisation.boxplot(os.path.join(self._sumocfg.rundir, "RelativeTimeLoss-{}_{}_vehicles_{}runs_one21segment.{}".format(p_scenarioname, l_stats.get("nbvehicles"), l_stats.get("nbruns"), "pdf")),
                                    l_stats.get("data").get("relativeLoss"),
                                    "{}:\nRelative time loss for ${}$ vehicles, ${}$ runs for each mode ({}),\none 2+1 segment, vtype distribution: {}".format(l_ttscenarioname, l_stats.get("nbvehicles"), l_stats.get("nbruns"), ", ".join(l_initialsortings), l_vtypedistribution),
                                    "initial ordering of vehicles (maximum speed)",
                                    "relative time loss in percent ($\\frac{\\mathrm{Traveltime}}{\\mathrm{Traveltime}-\\mathrm{Timeloss}}*100$)"
                                    )


    def runScenarios(self):
        for i_scenarioname in self._sumocfg.getRunConfig().get("scenarios"):
            self._runScenario(i_scenarioname)
