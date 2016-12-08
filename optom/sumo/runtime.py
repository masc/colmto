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
"""Runtime to control SUMO."""
from __future__ import division
from __future__ import print_function

import subprocess

import optom.common.log
import optom.environment.cse
try:
    import traci
except ImportError:
    raise ("please declare environment variable 'SUMO_HOME' as the root"
           "directory of your sumo installation (it should contain folders 'bin',"
           "'tools' and 'docs')")


class Runtime(object):
    """Runtime class"""
    # pylint: disable=too-few-public-methods
    def __init__(self, args, sumo_config, sumo_binary):
        """C'tor."""
        self._args = args
        self._sumo_config = sumo_config
        self._sumo_binary = sumo_binary
        self._log = optom.common.log.logger(__name__, args.loglevel, args.quiet, args.logfile)

    def run_once(self, run_config):
        """
        Run provided scenario in one shot.

        :param run_config Run configuration
        """

        self._log.info(
            "Running scenario %s: run %d",
            run_config.get("scenarioname"), run_config.get("runnumber")
        )
        l_sumoprocess = subprocess.check_output(
            [
                self._sumo_binary,
                "-c", run_config.get("configfile"),
                "--gui-settings-file", run_config.get("settingsfile"),
                "--time-to-teleport", "-1",
                "--no-step-log",
                "--fcd-output", run_config.get("fcdfile")
            ],
            stderr=subprocess.STDOUT,
            bufsize=-1
        )
        self._log.debug("%s : %s", self._sumo_binary, l_sumoprocess.replace("\n", ""))

    def run_traci(self, run_config, cse):
        """
        Run provided scenario with TraCI by providing a ref to an optimisation entity

        :param run_config Run configuration
        :param cse central optimisation entity
        """

        print("--remote-port", run_config.get("sumoport"))
        if not isinstance(cse, optom.environment.cse.BaseCSE):
            raise AttributeError

        subprocess.call(
            [
                self._sumo_binary,
                "-c", run_config.get("configfile"),
                "--gui-settings-file", run_config.get("settingsfile"),
                "--time-to-teleport", "-1",
                "--no-step-log",
                "--fcd-output", run_config.get("fcdfile"),
                "--remote-port", run_config.get("sumoport")
            ]
        )

        l_sumo_connection = traci.connect(run_config.get("sumoport"))

        for _ in xrange(100):
            l_sumo_connection.simulationStep()

        self._log.info(
            "Running scenario %s, run %d with TraCI",
            run_config.get("scenarioname"), run_config.get("runnumber")
        )
