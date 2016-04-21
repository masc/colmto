# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.pyplot as plt


class Visualisation(object):

    def getColormap(self, p_values, p_cmap):
        l_jet=plt.get_cmap(p_cmap)
        l_cnorm  = colors.Normalize(vmin=min(p_values), vmax=max(p_values))
        return cm.ScalarMappable(norm=l_cnorm, cmap=l_jet)

    def plotRunStats(self, p_vehiclecount, p_density, p_scenarioname, p_fname):
        xvc,yvc = zip(*p_vehiclecount)
        xdc,ydc = zip(*p_density)

        plt.figure(1)
        plt.title(p_scenarioname)

        plt.subplot(211)
        plt.plot(xvc,yvc,'b')
        plt.xlabel("Time steps")
        plt.ylabel("Number of vehicles")

        plt.subplot(212)
        plt.plot(xdc,ydc,'r')
        plt.xlabel("Time steps")
        plt.ylabel("Average density")

        plt.savefig(p_fname)
        plt.close()
