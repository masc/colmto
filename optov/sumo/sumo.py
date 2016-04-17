# -*- coding: utf-8 -*-
from __future__ import print_function
from runtime import runtime
from common.sumocfg import SumoConfig
from sumolib import checkBinary
import os
import traci
import sumolib

class Sumo(object):

    def __init__(self, p_args):
        self._sumocfg = SumoConfig(p_args, checkBinary("netconvert"), checkBinary("duarouter"))
        self._runtime = runtime.Runtime(self._sumocfg,
                                        checkBinary("sumo")
                                            if self._sumocfg.getConfig().getRunConfig().get("headless")
                                            else checkBinary("sumo-gui"))