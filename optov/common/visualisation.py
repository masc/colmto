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

    def plotAvgGlobalSatisfactionPrePost(self, p_scenarioname, p_runnumber, p_vehicles):
        plt.figure(1)
        plt.title("{}: run {}".format(p_scenarioname, p_runnumber))
        l_preotlsatisfaction=[]
        l_postotlsatisfaction=[]
        for i_vid, i_vehicle in p_vehicles.iteritems():
            l_vpresat=(0,0)
            l_vpostsat=(0,0)
            for i_timestep, i_result in i_vehicle.get("trajectory").iteritems():
                if i_result.get(tc.VAR_LANE_ID)=="2_1_segment_0":
                    l_vpresat=(i_timestep,i_result.get("satisfaction"))
                elif i_result.get(tc.VAR_LANE_ID)=="2_1_end-ramp_exit_0" and l_vpostsat == (0,0):
                    l_vpostsat=(i_timestep,i_result.get("satisfaction"))
            l_preotlsatisfaction.append(l_vpresat[1])
            l_postotlsatisfaction.append(l_vpostsat[1])

        plt.boxplot((l_preotlsatisfaction, l_postotlsatisfaction))
        plt.xlabel("Pre vs Post average satisfaction")
        plt.ylabel("Satisfaction in %")
        plt.savefig("{}-{}-AvgGlobalSatisfactionPrePost.pdf".format(p_scenarioname,p_runnumber))
        plt.savefig("{}-{}-AvgGlobalSatisfactionPrePost.png".format(p_scenarioname,p_runnumber))
        plt.close()

    def plotDensity(self, p_scenarioname, p_runnumber, p_density):
        plt.figure(1)
        plt.title("{}: run {}".format(p_scenarioname, p_runnumber))

        plt.plot(p_density, "b")
        plt.savefig("{}-{}-Density.pdf".format(p_scenarioname,p_runnumber))
        plt.savefig("{}-{}-Density.png".format(p_scenarioname,p_runnumber))
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
