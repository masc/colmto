# -*- coding: utf-8 -*-
# @package optom
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of Overtaking Manoeuvres project.   #
# # Copyright (c) 2016, Malte Aschermann (malte.aschermann@tu-clausthal.de)   #
# # This program is free software: you can redistribute it and/or modify      #
# # it under the terms of the GNU Lesser General Public License as            #
# # published by the Free Software Foundation, either version 3 of the        #
# # License, or (at your option) any later version.                           #
# #                                                                           #
# # This program is distributed in the hope that it will be useful,           #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# # GNU Lesser General Public License for more details.                       #
# #                                                                           #
# # You should have received a copy of the GNU Lesser General Public License  #
# # along with this program. If not, see http://www.gnu.org/licenses/         #
# #############################################################################
# @endcond
from __future__ import print_function
from __future__ import division
import subprocess
from optom.common import log


class Runtime(object):

    def __init__(self, p_args, p_sumoconfig, p_sumobinary):
        self._sumoconfig = p_sumoconfig
        self._sumobinary = p_sumobinary
        self._log = log.logger(__name__, p_args.loglevel, p_args.quiet, p_args.logfile)

    def run(self, p_runcfg, p_scenarioname, p_runnumber):
        self._log.info("Running scenario %s: run %d", p_scenarioname, p_runnumber)
        l_sumoprocess = subprocess.check_output(
            [
                self._sumobinary,
                "-c", p_runcfg.get("configfile"),
                "--gui-settings-file", p_runcfg.get("settingsfile"),
                "--time-to-teleport", "-1",
                "--no-step-log"
             ],
            stderr=subprocess.STDOUT,
            bufsize=-1
        )
        self._log.debug("%s : %s", self._sumobinary, l_sumoprocess.replace("\n", ""))
