from __future__ import print_function
from __future__ import division
import subprocess
import sys
import json

import traci
import sumolib
import traci.constants as tc


class Runtime(object):

    def __init__(self, p_sumoconfig, p_visualisation, p_sumobinary):
        self._sumoconfig = p_sumoconfig
        self._visualisation = p_visualisation
        self._sumobinary = p_sumobinary


    def run(self, p_scenario):
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

        l_vehiclesinstep = []
        l_globaldensity = []

        l_vehicles = {}

        # do simulation time steps as long as vehicles are present in the network
        while traci.simulation.getMinExpectedNumber() > 0:
            # tell SUMO to do a simulation step
            traci.simulationStep()

            if l_step % 1000 == 0:
                print("{}: Step {}".format(p_scenario, l_step))

            # get new vehicles
            l_departedVehicles = traci.simulation.getDepartedIDList()
            l_arrivedVehicles = traci.simulation.getArrivedIDList()
            l_newVehicles = set(l_departedVehicles).difference(l_arrivedVehicles).difference(set(l_vehicles.keys()))

            # subscribe new vehicles to to events
            for i_vid in l_newVehicles:
                #print("Subscribing new vehicle {} {}".format(i_vid, type(i_vid)))
                traci.vehicle.subscribe(
                    i_vid,
                    (
                        tc.VAR_SPEED,
                        tc.VAR_LANE_ID,
                        tc.VAR_LANE_INDEX,
                        tc.VAR_POSITION,
                    )
                )

                l_vehicles.update(
                    (i_vid, {"results" : {} }) for i_vid in l_newVehicles
                )

            # get subscription results for all vehicles in this step
            for i_vid in l_vehicles.iterkeys():
                l_vehicles.get(i_vid).get("results")[l_step] = traci.vehicle.getSubscriptionResults(i_vid)

            #l_nbvehicles = traci.vehicle.getIDCount()
            #l_vehiclesinstep.append( (l_step, l_nbvehicles ) )
            #l_globaldensity.append( (l_step, l_nbvehicles / (self._sumoconfig.getRoadwayConfig().get(p_scenario).get("parameters").get("length") / 5) ))



            l_step += 1


        print("\n\nSteps: {}".format(l_step))
        json.dump(l_vehicles, open(p_scenario+".json", "w"), sort_keys=False, indent=None, separators=(',', ':'))
        # for i_vid in l_vehicles.iterkeys():
        #     print(traci.vehicle.getSubscriptionResults(i_vid))
        # #self._visualisation.plotRunStats(l_vehiclesinstep, l_globaldensity, p_scenario, p_scenario+".png")

        # close the TraCI control loop
        traci.close()
        sys.stdout.flush()

        l_sumoprocess.wait()




