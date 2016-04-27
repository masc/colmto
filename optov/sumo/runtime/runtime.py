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

    def run(self, p_scenario, p_runnumber=0):
        l_scenario = self._sumoconfig.get("scenarios").get(p_scenario)
        l_sumoprocess = subprocess.Popen(
             [self._sumobinary,
              "-c", l_scenario.get("configfile"),
              "--tripinfo-output", l_scenario.get("tripinfofile"),
              "--gui-settings-file", l_scenario.get("settingsfile"),
              "--no-step-log",
              "--remote-port", str(self._sumoconfig.get("port"))
              ],
             stdout=sys.stdout,
             stderr=sys.stderr)
        # execute the TraCI control loop
        traci.init(self._sumoconfig.get("port"))

        l_step = 0

        l_runresults = {}
        l_activevehicleids = set()

        l_density = []

        # induct loop value subscription
        traci.inductionloop.subscribe(
            "start",
            (
                tc.LAST_STEP_VEHICLE_ID_LIST,
                tc.LAST_STEP_VEHICLE_DATA
            )
        )
        traci.inductionloop.subscribe(
            "exit",
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
                print("{}: Step {}, {} active vehicles".format(p_scenario, l_step, len(l_activevehicleids)))

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

                # create new vehicle objects
                # TODO: Initialise new vehicles objects on xml generation
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
            #print(l_step,l_inductionresults)
            for i_vid in l_inductionresults.get("start").get(tc.LAST_STEP_VEHICLE_ID_LIST):
                if l_inductionresults.get("start").get(tc.LAST_STEP_VEHICLE_DATA)[0][0] == i_vid:
                    l_entrytime = l_inductionresults.get("start").get(tc.LAST_STEP_VEHICLE_DATA)[0][2]
                    l_speed = l_runresults.get(i_vid).get("trajectory").get(l_step) #.get(tc.VAR_SPEED)
                    l_maxspeed = l_runresults.get(i_vid).get("trajectory").get(l_step) #.get(tc.VAR_MAXSPEED)
                    l_runresults.get(i_vid).get("inductionloop")["starttime"] = (l_entrytime, l_speed, l_maxspeed)

            for i_vid in l_inductionresults.get("exit").get(tc.LAST_STEP_VEHICLE_ID_LIST):
                if l_inductionresults.get("exit").get(tc.LAST_STEP_VEHICLE_DATA)[0][0] == i_vid:
                    l_entrytime = l_inductionresults.get("exit").get(tc.LAST_STEP_VEHICLE_DATA)[0][2]
                    l_speed = l_runresults.get(i_vid).get("trajectory").get(l_step) #.get(tc.VAR_SPEED)
                    l_maxspeed = l_runresults.get(i_vid).get("trajectory").get(l_step) #.get(tc.VAR_MAXSPEED)
                    l_runresults.get(i_vid).get("inductionloop")["exittime"] = (l_entrytime, l_speed, l_maxspeed)

            l_step += 1


        print("Steps: {}".format(l_step))

        #json.dump(l_vehicles, open(p_scenario+".json", "w"), sort_keys=False, indent=None, separators=(',', ':'))
        # for i_vid in l_vehicles.iterkeys():
        #     print(traci.vehicle.getSubscriptionResults(i_vid))
        # #self._visualisation.plotRunStats(l_vehiclesinstep, l_globaldensity, p_scenario, p_scenario+".png")

        # close the TraCI control loop
        traci.close()
        sys.stdout.flush()

        l_sumoprocess.wait()
        self._visualisation.plotDensity(p_scenario, p_runnumber, l_density)
        return l_runresults


