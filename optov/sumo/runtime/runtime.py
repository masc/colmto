# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
import subprocess
import sys
import numpy as np

import traci
import sumolib
import traci.constants as tc


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
        l_sumoprocess.wait()

    def runTraci(self, p_scenario):
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


        l_runresults = self._iterateTraci(p_scenario)


        # close the TraCI control loop
        traci.close()
        sys.stdout.flush()

        l_sumoprocess.wait()
        return l_runresults

    def _iterateTraci(self, p_scenario):
        # execute the TraCI control loop
        traci.init(self._sumoconfig.get("port"))

        l_step = 0

        l_runresults = {}
        l_activevehicleids = set()

        l_density = []

        # induct loop value subscription
        traci.inductionloop.subscribe(
            "pre",
            (
                tc.LAST_STEP_VEHICLE_ID_LIST,
                tc.LAST_STEP_VEHICLE_DATA
            )
        )
        traci.inductionloop.subscribe(
            "post",
            (
                tc.LAST_STEP_VEHICLE_ID_LIST,
                tc.LAST_STEP_VEHICLE_DATA
            )
        )

        # do simulation time steps as long as vehicles are present in the network
        while traci.simulation.getMinExpectedNumber() > 0:
            # tell SUMO to do a simulation step
            traci.simulationStep()

            # get new vehicles
            l_departedvehicleids = traci.simulation.getDepartedIDList()
            l_arrivedvehiclesids = traci.simulation.getArrivedIDList()
            l_activevehicleids = l_activevehicleids.union(l_departedvehicleids).difference(l_arrivedvehiclesids)

            if l_step % 1000 == 0:
                print("{}: Step {}, {} active vehicles".format(p_scenarioname, l_step, len(l_activevehicleids)))

            # subscribe newly departed vehicles to events
            for i_vid in l_departedvehicleids:
                traci.vehicle.subscribe(
                    i_vid,
                    (
                        tc.VAR_SPEED,
                        tc.VAR_MAXSPEED,
                        tc.VAR_LANE_ID,
                        tc.VAR_LANE_INDEX,
                        tc.VAR_POSITION,
                        tc.VAR_LENGTH
                    )
                )

                l_runresults.update(
                    (i_vid, {"length": 0, "trajectory": {}, "inductionloop": {} }) for i_vid in l_departedvehicleids
                )

            # update subscription results for all active vehicles in this step
            for i_vid in l_activevehicleids:
                l_results = traci.vehicle.getSubscriptionResults(i_vid)
                l_results["satisfaction"] = l_results.get(tc.VAR_SPEED)/l_results.get(tc.VAR_MAXSPEED)
                l_runresults.get(i_vid)["length"] = l_results.pop(tc.VAR_LENGTH)
                l_runresults.get(i_vid).get("trajectory")[l_step] = l_results

            #l_nbvehicles = traci.vehicle.getIDCount()
            #l_vehiclesinstep.append( (l_step, l_nbvehicles ) )
            #l_globaldensity.append( (l_step, l_nbvehicles / (self._sumoconfig.getScenarioConfig().get(p_scenario).get("parameters").get("length") / 5) ))

            l_totalroadlength = self._sumoconfig.getScenarioConfig().get(p_scenario).get("parameters").get("length")
            l_density.append(
                sum(map(lambda v: l_runresults.get(v).get("length"), l_activevehicleids))/l_totalroadlength
            )

            # induct loop value retrieval
            l_inductionresults = traci.inductionloop.getSubscriptionResults()
            for i_vid in l_inductionresults.get("pre").get(tc.LAST_STEP_VEHICLE_ID_LIST):
                if l_inductionresults.get("pre").get(tc.LAST_STEP_VEHICLE_DATA)[0][0] == i_vid:
                    l_entrytime = l_inductionresults.get("pre").get(tc.LAST_STEP_VEHICLE_DATA)[0][2]
                    if l_runresults.get(i_vid).get("inductionloop").get("pre") == None:
                        l_runresults.get(i_vid).get("inductionloop")["pre"] = {"entrytime": l_entrytime, "step" : l_step}

            for i_vid in l_inductionresults.get("post").get(tc.LAST_STEP_VEHICLE_ID_LIST):
                if l_inductionresults.get("post").get(tc.LAST_STEP_VEHICLE_DATA)[0][0] == i_vid:
                    l_entrytime = l_inductionresults.get("post").get(tc.LAST_STEP_VEHICLE_DATA)[0][2]
                    if l_runresults.get(i_vid).get("inductionloop").get("post") == None:
                        l_runresults.get(i_vid).get("inductionloop")["post"] = {"entrytime": l_entrytime, "step" : l_step}

            l_step += 1


        print("Steps: {}".format(l_step))
        return l_results

