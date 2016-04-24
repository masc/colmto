# -*- coding: utf-8 -*-
from __future__ import print_function

import traci
import sumolib

from configuration.sumocfg import SumoConfig
from sumolib import checkBinary

from runtime.runtime import Runtime
from common.visualisation import Visualisation
from common.resultswriter import ResultsWriter
from common.statistics import Statistics


class Sumo(object):

    def __init__(self, p_args):
        self._visualisation = Visualisation()
        self._resultswriter = ResultsWriter()
        self._statistics = Statistics()
        self._sumocfg = SumoConfig(p_args, self._visualisation, checkBinary("netconvert"), checkBinary("duarouter"))
        self._runtime = Runtime(self._sumocfg, self._visualisation,
                                        checkBinary("sumo")
                                            if self._sumocfg.get("headless")
                                            else checkBinary("sumo-gui"))

    def runScenarios(self, p_scenarios=tuple()):
        for i_scenario in p_scenarios:
            l_runresults = {}
            for i_run in xrange(self._sumocfg.get("runs")):
                l_runresults[i_run] = self._runtime.run(i_scenario, i_run)

            # push results to resultswriter and statistics for dumping data and plotting fancy figures
            self._resultswriter.dumpSUMOResults(i_scenario, l_runresults)
            self._statistics.pushSUMOResults(i_scenario, l_runresults)

    def runAllScenarios(self):
        self.runScenarios(self._sumocfg.get("scenarios").keys())
