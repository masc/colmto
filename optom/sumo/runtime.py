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
import optom.cse.cse
import numpy

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
        Args:
            run_config: run configuration object
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
        Args:
            run_config: run configuration
            cse: central optimisation entity object optom.cse.cse.SumoCSE
        """

        if not isinstance(cse, optom.cse.cse.SumoCSE):
            raise AttributeError("Provided CSE object is not of type SumoCSE.")

        self._log.debug("starting sumo process")
        self._log.debug("CSE %s with policies %s", cse, cse.policies)
        traci.start(
            [
                self._sumo_binary,
                "-c", run_config.get("configfile"),
                "--gui-settings-file", run_config.get("settingsfile"),
                "--time-to-teleport", "-1",
                "--no-step-log",
                "--fcd-output", run_config.get("fcdfile")
            ]
        )
        self._log.debug("connecting to TraCI instance on port %d", run_config.get("sumoport"))

        l_arrived_count = 0

        while traci.vehicle.getIDCount() > 0 or l_arrived_count == 0:
            l_arrived_count += traci.simulation.getArrivedNumber()

            self._log.debug("new vehicles: %s", traci.simulation.getDepartedIDList())

            # iterate through every vehicle id currently active in simulation
            for i_vehicle_id in traci.vehicle.getIDList():
                # update vehicle position
                run_config.get("vehicles").get(i_vehicle_id).position = numpy.array(
                    traci.vehicle.getPosition(i_vehicle_id)
                )

                # set vclass according to policies for each new entering vehicle, i.e.
                # allow vehicles access to OTL depending on policy
                cse.apply_one(run_config.get("vehicles").get(i_vehicle_id))
                # update vehicle class via traci if changed
                if traci.vehicle.getVehicleClass(
                        i_vehicle_id
                ) != run_config.get("vehicles").get(i_vehicle_id).vehicle_class:
                    traci.vehicle.setVehicleClass(
                        i_vehicle_id,
                        run_config.get("vehicles").get(i_vehicle_id).vehicle_class
                    )

            traci.simulationStep()

        traci.close()

        self._log.info(
            "TraCI run of scenario %s, run %d completed.",
            run_config.get("scenarioname"), run_config.get("runnumber")
        )
