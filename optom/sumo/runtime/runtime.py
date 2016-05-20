# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
import subprocess
import sys
import os
import logging
import cStringIO

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

    def run(self, p_runcfg, p_scenarioname, p_runnumber):
        self._log.info("Running scenario {}: run {}".format(p_scenarioname, p_runnumber))
        with open(os.devnull, "w") as f_null:
            l_sumoprocess = subprocess.Popen(
                [self._sumobinary,
                 "-c", p_runcfg.get("configfile"),
                 "--tripinfo-output", p_runcfg.get("tripinfofile"),
                 "--fcd-output", p_runcfg.get("fcdfile"),
                 "--gui-settings-file", p_runcfg.get("settingsfile"),
                 "--time-to-teleport", "-1",
                 "--no-step-log"
                 ],
                stdout=f_null,
                stderr=f_null,
                bufsize=-1)
            l_sumoprocess.wait()

