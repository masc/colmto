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

    def runScenario(self, p_scenario):
        if self._sumocfg.getScenarioConfig().get(p_scenario) == None:
            print("/!\ scenario {} not found in configuration".format(p_scenario))
            return

        for i_run in xrange(self._sumocfg.getRunConfig().get("runs")):
            l_scenario = self._sumocfg.generateScenario(p_scenario, i_run)
            self._runtime.run(l_scenario)
            self._statistics.traveltimes(l_scenario)



    def runScenarios(self, p_scenarios=tuple()):
        for i_scenario in p_scenarios:
            self.runScenario(i_scenario)

    def runAllScenarios(self):
        self.runScenarios(self._sumocfg.getScenarioConfig().keys())
