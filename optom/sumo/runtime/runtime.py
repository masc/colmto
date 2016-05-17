# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
import subprocess
import sys

class Runtime(object):

    def __init__(self, p_sumoconfig, p_visualisation, p_sumobinary):
        self._sumoconfig = p_sumoconfig
        self._visualisation = p_visualisation
        self._sumobinary = p_sumobinary

    def run(self, p_scenario):
        l_sumoprocess = subprocess.Popen(
            [self._sumobinary,
             "-c", p_scenario.get("configfile"),
             "--tripinfo-output", p_scenario.get("tripinfofile"),
             "--fcd-output", p_scenario.get("fcdfile"),
             "--gui-settings-file", p_scenario.get("settingsfile"),
             "--no-step-log"
             ],
            stdout=sys.stdout,
            stderr=sys.stderr)
        sys.stdout.flush()
        l_sumoprocess.wait()

