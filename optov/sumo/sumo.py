# -*- coding: utf-8 -*-
from __future__ import print_function
from runtime.runtime import Runtime
from common.sumocfg import SumoConfig
from sumolib import checkBinary
import os
import traci
import sumolib

class Sumo(object):

    def __init__(self, p_args):
        self._sumocfg = SumoConfig(p_args, checkBinary("netconvert"), checkBinary("duarouter"))
        self._runtime = Runtime(self._sumocfg,
                                        checkBinary("sumo")
                                            if self._sumocfg.get("headless")
                                            else checkBinary("sumo-gui"))

    def runScenarios(self, p_scenarios=[]):
        for i_scenario in p_scenarios:
            self._runtime.run(i_scenario)

    def runAllScenarios(self):
        self.runScenarios(self._sumocfg.get("scenarios").keys())
