# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
import subprocess
from common import log

class Runtime(object):

    def __init__(self, p_args, p_sumoconfig, p_visualisation, p_sumobinary):
        self._sumoconfig = p_sumoconfig
        self._visualisation = p_visualisation
        self._sumobinary = p_sumobinary
        self._log = log.logger(p_args, __name__)

    def run(self, p_runcfg, p_scenarioname, p_runnumber):
        self._log.info("Running scenario {}: run {}".format(p_scenarioname, p_runnumber))
        l_sumoprocess = subprocess.check_output(
            [
                self._sumobinary,
                "-c", p_runcfg.get("configfile"),
                "--tripinfo-output", p_runcfg.get("tripinfofile"),
                "--fcd-output", p_runcfg.get("fcdfile"),
                "--gui-settings-file", p_runcfg.get("settingsfile"),
                "--time-to-teleport", "-1",
                "--no-step-log"
             ],
            stderr=subprocess.STDOUT,
            bufsize=-1
        )
        self._log.info("{}: {}".format(self._sumobinary,l_sumoprocess.replace("\n","")))
        self._log.info("Finished run {}".format(p_runnumber))

