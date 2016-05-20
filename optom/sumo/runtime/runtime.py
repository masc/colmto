# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
import subprocess
import sys
import logging

class Runtime(object):

    def __init__(self, p_args, p_sumoconfig, p_visualisation, p_sumobinary):
        self._sumoconfig = p_sumoconfig
        self._visualisation = p_visualisation
        self._sumobinary = p_sumobinary

        self._log = logging.getLogger(__name__)
        self._log.setLevel(p_args.loglevel)

        # create a file handler
        handler = logging.FileHandler(p_args.logfile)
        handler.setLevel(p_args.loglevel)

        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # add the handlers to the logger
        self._log.addHandler(handler)

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
            stderr=sys.stderr) # TODO: stdout/err to logger info/error
        sys.stdout.flush()
        l_sumoprocess.wait()

