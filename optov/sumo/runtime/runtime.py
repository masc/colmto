from __future__ import print_function
from __future__ import division
import subprocess
import sys
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import traci
import sumolib


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

        # do simulation time steps as long as vehicles are present in the network
        while traci.simulation.getMinExpectedNumber() > 0:

            l_nbvehicles = traci.vehicle.getIDCount()
            l_vehiclesinstep.append( (l_step, l_nbvehicles ) )
            l_globaldensity.append( (l_step, l_nbvehicles / (self._sumoconfig.getRoadwayConfig().get(p_scenario).get("parameters").get("length") / 5) ))
            # tell SUMO to do a simulation step
            traci.simulationStep()
            l_step += 1


        print("\n\nSteps: {}".format(l_step))

        self._visualisation.plotRunStats(l_vehiclesinstep, l_globaldensity, p_scenario, p_scenario+".png")

        # close the TraCI control loop
        traci.close()
        sys.stdout.flush()

        l_sumoprocess.wait()




