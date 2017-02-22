# -*- coding: utf-8 -*-
# @package optom
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of Overtaking Manoeuvres project.   #
# # Copyright (c) 2017, Malte Aschermann (malte.aschermann@tu-clausthal.de)   #
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
        @brief Run provided scenario in one shot.

        @param run_config run configuration object
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

        @param run_config run configuration
        @param cse central optimisation entity instance of optom.cse.cse.SumoCSE

        @retval list of vehicles, containing travel stats
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
                "--no-step-log"
            ]
        )
        self._log.debug("connecting to TraCI instance on port %d", run_config.get("sumoport"))

        # subscribe to global simulation vars
        traci.simulation.subscribe(
            [
                traci.constants.VAR_TIME_STEP,
                traci.constants.VAR_DEPARTED_VEHICLES_IDS,
                traci.constants.VAR_ARRIVED_VEHICLES_IDS,
                traci.constants.VAR_MIN_EXPECTED_VEHICLES
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

        # initial fetch of subscription results
        l_results_simulation = traci.simulation.getSubscriptionResults()

        # main loop through traci driven simulation runs
        while l_results_simulation.get(traci.constants.VAR_MIN_EXPECTED_VEHICLES) > 0:

            # set initial attribute start_time of newly entering vehicles
            # and subscribe to parameters
            for i_vehicle_id in l_results_simulation.get(traci.constants.VAR_DEPARTED_VEHICLES_IDS):

                # set TraCI -> vehicle.start_time
                run_config.get("vehicles").get(i_vehicle_id).start_time = \
                    l_results_simulation.get(traci.constants.VAR_TIME_STEP)/10.**3

                # subscribe to parameters
                traci.vehicle.subscribe(
                    i_vehicle_id, [
                        traci.constants.VAR_POSITION,
                        traci.constants.VAR_LANE_INDEX,
                        traci.constants.VAR_VEHICLECLASS,
                        traci.constants.VAR_MAXSPEED,
                        traci.constants.VAR_SPEED
                    ]
                )

            # retrieve results, update vehicle objects, apply cse policies
            for i_vehicle_id, i_results in traci.vehicle.getSubscriptionResults().iteritems():

                # vehicle object corresponding to current vehicle fetched from traci
                l_vehicle = run_config.get("vehicles").get(i_vehicle_id)

                # set vclass according to policies for each vehicle, i.e.
                # allow vehicles access to OTL depending on policy
                cse.apply_one(

                    # update vehicle position and speed
                    l_vehicle.update(
                        i_results.get(traci.constants.VAR_POSITION),
                        i_results.get(traci.constants.VAR_LANE_INDEX),
                        i_results.get(traci.constants.VAR_SPEED)
                    )

                )

                # update vehicle class via traci if vclass changed due to applying CSE
                if i_results.get(traci.constants.VAR_VEHICLECLASS) != l_vehicle.vehicle_class:
                    traci.vehicle.setVehicleClass(
                        i_vehicle_id,
                        l_vehicle.vehicle_class
                    )
                    if l_vehicle.vehicle_class == optom.cse.policy.SUMOPolicy.to_disallowed_class():
                        traci.vehicle.setColor(
                            i_vehicle_id,
                            (255, 0, 0, 255)
                        )
                    else:
                        traci.vehicle.setColor(
                            i_vehicle_id,
                            tuple(l_vehicle.color)
                        )

                # record travel stats to vehicle
                l_vehicle.record_travel_stats(
                    l_results_simulation.get(traci.constants.VAR_TIME_STEP)/10.**3
                )

                # if i_vehicle_id == "vehicle10":
                #     self._log.debug(
                #         "pos: %s, %s, act TT: %s, opt TT: %s, time loss: %s (%s pct.), dsat: %s",
                #         l_vehicle.position,
                #         l_vehicle.grid_position,
                #         l_vehicle.travel_time,
                #         round(l_vehicle.position[0] / l_vehicle.speed_max, 2),
                #         round(l_vehicle.travel_stats.get("step").get("time_loss")[-1], 2),
                #         round(
                #             l_vehicle.travel_stats.get("step").get("time_loss")[-1] /
                #             (l_vehicle.position[0] / l_vehicle.speed_max) * 100,
                #             2
                #         ),
                #         round(l_vehicle.travel_stats.get("step").get("dissatisfaction")[-1], 32)
                #     )

            traci.simulationStep()

            # fetch new results for next simulation step/cycle
            l_results_simulation = traci.simulation.getSubscriptionResults()

        traci.close()

        self._log.info(
            "TraCI run of scenario %s, run %d completed.",
            run_config.get("scenarioname"), run_config.get("runnumber")
        )

        return run_config.get("vehicles")

    # pylint: enable=too-few-public-methods
