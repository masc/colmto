# -*- coding: utf-8 -*-
from __future__ import print_function

from configuration.sumocfg import SumoConfig
from sumolib import checkBinary

from runtime.runtime import Runtime
from common.visualisation import Visualisation
from common.resultswriter import ResultsWriter
from common.statistics import Statistics

import os

class Sumo(object):

    def __init__(self, p_args):
        self._visualisation = Visualisation()
        self._resultswriter = ResultsWriter()
        self._statistics = Statistics()
        self._scenarioruns = {} # map scenarios -> runid -> files
        self._sumocfg = SumoConfig(p_args, self._visualisation, checkBinary("netconvert"), checkBinary("duarouter"))
        self._runtime = Runtime(self._sumocfg, self._visualisation,
                                        checkBinary("sumo")
                                            if self._sumocfg.get("headless")
                                            else checkBinary("sumo-gui"))

    def runScenario(self, p_scenarioname):
        if self._sumocfg.getScenarioConfig().get(p_scenarioname) == None:
            print("/!\ scenario {} not found in configuration".format(p_scenarioname))
            return

        self._scenarioruns[p_scenarioname] = {}
        for i_initialsorting in self._sumocfg.getRunConfig().get("initialsortings"):

            self._scenarioruns.get(p_scenarioname)[i_initialsorting] = {}

            for i_run in xrange(self._sumocfg.getRunConfig().get("runs")):
                l_scenario = self._sumocfg.generateScenario(p_scenarioname, i_initialsorting, i_run)
                self._scenarioruns.get(p_scenarioname).get(i_initialsorting)[i_run] = l_scenario
                self._runtime.run(l_scenario)
        # dump scenarioruns to json file
        self._resultswriter.writeJson(self._scenarioruns.get(p_scenarioname), os.path.join(self._sumocfg.getSUMOConfigDir(), "runs-{}.json".format(p_scenarioname)))
        l_travelstats = self._statistics.traveltimes(p_scenarioname, self._scenarioruns.get(p_scenarioname))
        l_timestats = self._statistics.traveltimes(p_scenarioname, self._scenarioruns.get(p_scenarioname))
        self._visualisation.boxplot(os.path.join(self._sumocfg.getSUMOConfigDir(), "Traveltime-{}_{}_vehicles_{}runs_one21segment.{}".format(p_scenarioname, l_travelstats.get("nbvehicles"), l_travelstats.get("nbruns"), "pdf")),
                                    l_travelstats.get("data"),
                                    "{}: Travel time for \n{} vehicles, {} runs for each mode, one 2+1 segment".format(p_scenarioname, l_travelstats.get("nbvehicles"), l_travelstats.get("nbruns")),
                                    "configuration modes (initial sorting)",
                                    "traveltime in seconds"
                                    )
        self._visualisation.boxplot(os.path.join(self._sumocfg.getSUMOConfigDir(), "TimeLoss-{}_{}_vehicles_{}runs_one21segment.{}".format(p_scenarioname, l_timestats.get("nbvehicles"), l_timestats.get("nbruns"), "pdf")),
                                    l_timestats.get("data"),
                                    "{}: Time loss for \n{} vehicles, {} runs for each mode, one 2+1 segment".format(p_scenarioname, l_timestats.get("nbvehicles"), l_timestats.get("nbruns")),
                                    "configuration modes (initial sorting)",
                                    "time loss in seconds"
                                    )


    def runScenarios(self, p_scenarios=tuple()):
        for i_scenario in p_scenarios:
            self.runScenario(i_scenario)

    def runAllScenarios(self):
        self.runScenarios(self._sumocfg.getScenarioConfig().keys())
