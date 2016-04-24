# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
import subprocess
import sys
import numpy as np
from visualisation import Visualisation
import traci.constants as tc

class Statistics(object):

    def __init__(self):
        self._visualisation = Visualisation()

    def pushSUMOResults(self, p_scenario, p_results):
        for i_vid, i_vobj in p_results.iteritems():
            l_vtraj = i_vobj.get("trajectory")


    def _density(self, p_scenario, p_run, p_results):
        pass

    def _satisfaction(self, p_scenario, p_run, p_results):
        pass



