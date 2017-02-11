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
        Run provided scenario with TraCI by providing a ref to an optimisation entity.

        Args:
            run_config: run configuration
            cse: central optimisation entity instance of optom.cse.cse.SumoCSE
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

        # subscribe to global simulation vars
        traci.simulation.subscribe(
            [
                traci.constants.VAR_TIME_STEP
            ]
        )

        # add polygon of otl denied positions if --gui enabled
        # and cse contains instance objects of optom.cse.policy.SUMOPositionPolicy
        if self._args.gui:
            for i_policy in cse.policies:
                if isinstance(i_policy, optom.cse.policy.SUMOPositionPolicy):
                    traci.polygon.add(
                        polygonID=str(i_policy),
                        shape=(
                            (i_policy.position_bbox[0][0], 2*(i_policy.position_bbox[0][1])+10),
                            (i_policy.position_bbox[1][0], 2*(i_policy.position_bbox[0][1])+10),
                            (i_policy.position_bbox[1][0], 2*(i_policy.position_bbox[1][1])+10),
                            (i_policy.position_bbox[0][0], 2*(i_policy.position_bbox[1][1])+10)
                        ),
                        color=(255, 0, 0, 255),
                        fill=True,
                    )

        # main loop through traci driven simulation runs
        while traci.simulation.getMinExpectedNumber() > 0:

            l_sim_current_time = traci.simulation.getSubscriptionResults().get(
                traci.constants.VAR_TIME_STEP
            )

            # subscribe to values of newly entering vehicles
            for i_vehicle_id in traci.simulation.getDepartedIDList():
                run_config.get("vehicles").get(i_vehicle_id).start_time = l_sim_current_time/10.**3
                traci.vehicle.subscribe(
                    i_vehicle_id, [
                        traci.constants.VAR_POSITION,
                        traci.constants.VAR_VEHICLECLASS,
                        traci.constants.VAR_MAXSPEED,
                    ]
                )

            # retrieve results, update vehicle objects, apply cse policies
            for i_vehicle_id, i_results in traci.vehicle.getSubscriptionResults().iteritems():
                # update vehicle position
                run_config.get("vehicles").get(i_vehicle_id).position = numpy.array(
                    i_results.get(traci.constants.VAR_POSITION)
                )

                # set vclass according to policies for each vehicle, i.e.
                # allow vehicles access to OTL depending on policy
                cse.apply_one(run_config.get("vehicles").get(i_vehicle_id))

                # update vehicle class via traci if vclass changed
                if i_results.get(traci.constants.VAR_VEHICLECLASS) \
                        != run_config.get("vehicles").get(i_vehicle_id).vehicle_class:
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
