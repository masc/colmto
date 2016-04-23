# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
import subprocess
import sys
from common.resultswriter import ResultsWriter

import traci
import sumolib
import traci.constants as tc


class Runtime(object):

    def __init__(self, p_sumoconfig, p_visualisation, p_sumobinary):
        self._sumoconfig = p_sumoconfig
        self._visualisation = p_visualisation
        self._sumobinary = p_sumobinary
        self._resultswriter = ResultsWriter()

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


        l_vehicles = {}
        l_activevehicleids = set()

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
                    )
                )

                # create new vehicle objects
                l_vehicles.update(
                    (i_vid, {"trajectory" : {} }) for i_vid in l_departedvehicleids
                )

            # update subscription results for all active vehicles in this step
            for i_vid in l_activevehicleids:
                l_results = traci.vehicle.getSubscriptionResults(i_vid)
                l_results["satisfaction"] = l_results.get(tc.VAR_SPEED)/l_results.get(tc.VAR_MAXSPEED)
                l_vehicles.get(i_vid).get("trajectory")[l_step] = l_results

            #l_nbvehicles = traci.vehicle.getIDCount()
            #l_vehiclesinstep.append( (l_step, l_nbvehicles ) )
            #l_globaldensity.append( (l_step, l_nbvehicles / (self._sumoconfig.getRoadwayConfig().get(p_scenario).get("parameters").get("length") / 5) ))

            l_step += 1


        print("\n\nSteps: {}".format(l_step))

        self._resultswriter.writeJsonCompact(l_vehicles, p_scenario+".json.gz")

        #json.dump(l_vehicles, open(p_scenario+".json", "w"), sort_keys=False, indent=None, separators=(',', ':'))
        # for i_vid in l_vehicles.iterkeys():
        #     print(traci.vehicle.getSubscriptionResults(i_vid))
        # #self._visualisation.plotRunStats(l_vehiclesinstep, l_globaldensity, p_scenario, p_scenario+".png")

        # close the TraCI control loop
        traci.close()
        sys.stdout.flush()

        l_sumoprocess.wait()




