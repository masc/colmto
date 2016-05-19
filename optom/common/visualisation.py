# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import traci.constants as tc
import math
import numpy as np

class Visualisation(object):

    def getColormap(self, p_values, p_cmap):
        l_jet=plt.get_cmap(p_cmap)
        l_cnorm  = colors.Normalize(vmin=min(p_values), vmax=max(p_values))
        return cm.ScalarMappable(norm=l_cnorm, cmap=l_jet)

    def plotDensity(self, p_scenarioname, p_density):
        pass

    def plotTraveltimes(self, p_scenarioname, p_runconfig, p_results):
        l_nbsteps=0
        l_nbvehicles = len(p_results)
        l_traveltimes = []
        l_initialsorting = p_runconfig.get("initialsorting")
        for i_vid, i_vehicle in p_results.iteritems():
            l_nbsteps = max(i_vehicle.get("trajectory").keys())
            for i_timestep, i_result in i_vehicle.get("trajectory").iteritems():
                l_traveltimes.append(i_result.get("inductionloop").get("traveltime"))
        plt.figure(1)
        plt.title("{}: {} vehicles, {} steps, runs {}, {}".format(p_scenarioname, l_nbvehicles, l_nbsteps))
        plt.boxplot(l_traveltimes)
        plt.xlabel("{}".format(l_initialsorting))
        plt.ylabel("traveltime in seconds")
        plt.savefig("{}-{}-{}-traveltime.pdf".format(p_scenarioname,l_nbsteps,l_initialsorting))
        plt.savefig("{}-{}-{}-traveltime.png".format(p_scenarioname,l_nbsteps,l_initialsorting))
        plt.close()

    def plotAvgGlobalSatisfactionPrePost(self, p_scenarioname, p_runnumber, p_vehicles):
        l_nbsteps = 0
        l_nbvehicles = len(p_vehicles)
        l_preotlsatisfaction=[]
        l_postotlsatisfaction=[]
        for i_vid, i_vehicle in p_vehicles.iteritems():
            l_vpresat=(0,0)
            l_vpostsat=(0,0)
            l_nbsteps = max(i_vehicle.get("trajectory").keys())
            for i_timestep, i_result in i_vehicle.get("trajectory").iteritems():
                if i_result.get(tc.VAR_LANE_ID)=="2_1_segment_0":
                    l_vpresat=(i_timestep,i_result.get("satisfaction"))
                elif i_result.get(tc.VAR_LANE_ID)=="2_1_end-ramp_exit_0" and l_vpostsat == (0,0):
                    l_vpostsat=(i_timestep,i_result.get("satisfaction"))
            l_preotlsatisfaction.append(l_vpresat[1])
            l_postotlsatisfaction.append(l_vpostsat[1])

        plt.figure(1)
        plt.title("{}: {} vehicles, {} steps, run {}".format(p_scenarioname, l_nbvehicles, l_nbsteps, p_runnumber))
        plt.boxplot((l_preotlsatisfaction, l_postotlsatisfaction))
        plt.xlabel("Pre vs Post satisfaction")
        plt.ylabel("Satisfaction in %")
        plt.savefig("{}-{}-{}-AvgGlobalSatisfactionPrePost.pdf".format(p_scenarioname,p_runnumber,l_nbsteps))
        plt.savefig("{}-{}-{}-AvgGlobalSatisfactionPrePost.png".format(p_scenarioname,p_runnumber,l_nbsteps))
        plt.close()

    def plotDensity(self, p_scenarioname, p_runnumber, p_density):
        plt.figure(1)
        plt.title("{}: run {}".format(p_scenarioname, p_runnumber))

        plt.plot(p_density, "b")
        plt.savefig("{}-{}-{}-Density.pdf".format(p_scenarioname,p_runnumber,len(p_density)))
        plt.savefig("{}-{}-{}-Density.png".format(p_scenarioname,p_runnumber,len(p_density)))
        plt.close()

    def boxplot(self, p_filename, p_data, p_title="", p_xlabel="", p_ylabel=""):
        plt.figure(1)

        l_datakeys = sorted(p_data.keys())
        l_data = [p_data.get(i_key) for i_key in l_datakeys]

        plt.title(p_title, fontsize=12)
        plt.xlabel(p_xlabel, fontsize=10)
        plt.ylabel(p_ylabel, fontsize=10)
        plt.boxplot(l_data, vert=True, notch=False, labels=l_datakeys)
        plt.savefig(p_filename)
        plt.close()

    def plotRunStats(self, p_vehiclecount, p_density, p_scenarioname, p_fname):
        xvc,yvc = zip(*p_vehiclecount)
        xdc,ydc = zip(*p_density)

        plt.figure(1)

        plt.subplot(211)
        plt.title(p_scenarioname)
        plt.plot(xvc,yvc,'b')
        plt.axis([0,max(xvc),0,max(yvc)])
        plt.xlabel("Time steps")
        plt.ylabel("Number of vehicles")

        plt.subplot(212)
        plt.plot(xdc,ydc,'r')
        plt.axis([0,max(xdc),0,1])
        plt.xlabel("Time steps")
        plt.ylabel("Average density")

        plt.savefig(p_fname)
        plt.close()
