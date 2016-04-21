# -*- coding: utf-8 -*-
from __future__ import print_function

import traci
import sumolib

from common.sumocfg import SumoConfig
from sumolib import checkBinary

from runtime.runtime import Runtime
from common.visualisation import Visualisation


class Sumo(object):

    def __init__(self, p_args):
        self._visualisation = Visualisation()
        self._sumocfg = SumoConfig(p_args, self._visualisation, checkBinary("netconvert"), checkBinary("duarouter"))
        self._runtime = Runtime(self._sumocfg, self._visualisation,
                                        checkBinary("sumo")
                                            if self._sumocfg.get("headless")
                                            else checkBinary("sumo-gui"))

    def runScenarios(self, p_scenarios=tuple()):
        for i_scenario in p_scenarios:
            self._runtime.run(i_scenario)

    def runAllScenarios(self):
        self.runScenarios(self._sumocfg.get("scenarios").keys())
