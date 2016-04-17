from __future__ import print_function
from __future__ import division
import subprocess
import os
import sys

class Runtime(object):

    def __init__(self, p_sumoconfig, p_sumobinary):
        self._sumoconfig = p_sumoconfig
        self._sumobinary = p_sumobinary

    def run(self):
        pass
        # l_sumoProcess = subprocess.Popen(
        #     [self._sumobinary,
        #      "-n", self.,
        #      "-r", os.path.join(self._config.getCfg("simulation").get("resourcedir"), self._routefile),
        #      "--tripinfo-output", os.path.join(self._config.getCfg("simulation").get("resourcedir"), "tripinfo.xml"),
        #      "--gui-settings-file", os.path.join(self._config.getCfg("simulation").get("resourcedir"), "gui-settings.cfg"),
        #      #"--no-step-log",
        #      "--remote-port", str(self._config.getCfg("simulation").get("sumoport"))],
        #     stdout=sys.stdout,
        #     stderr=sys.stderr)