# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
import subprocess
import sys
import numpy as np
import xml.etree.ElementTree as ElementTree

from visualisation import Visualisation
import traci.constants as tc

class Statistics(object):

    def __init__(self):
        self._visualisation = Visualisation()

    def pushSUMOResults(self, p_scenario, p_runconfig, p_results):
        for i_runid, i_runobj in p_results.iteritems():
            self._visualisation.plotAvgGlobalSatisfactionPrePost(p_scenario, i_runid, i_runobj)
            self._visualisation.plotTraveltimes(p_scenario, p_runconfig, i_runobj)

            # for i_vid, i_vobj in i_runobj.iteritems():
            #     l_vtraj = i_vobj.get("trajectory")
            #     self._visualisation.plotRunStats()

    def _density(self, p_scenario, p_run, p_results):
        pass

    def _satisfaction(self, p_scenario, p_run, p_results):
        pass

    def traveltimes(self, p_scenarioname, p_scenarioruns):
        print("* traveltime statistics for scenario {}".format(p_scenarioname))

        l_traveltimes = { "best" : [],
                          "worst" : [],
                          "random": []
                          }
        l_timeloss = { "best" : [],
                       "worst" : [],
                       "random": []
                       }

        l_runs = 0
        l_vehicles = 0
        for i_sortingmode, i_scenarioruns in p_scenarioruns.iteritems():
            l_runs = len(i_scenarioruns)
            for i_run, i_scenariorun in i_scenarioruns.iteritems():
                l_ettripinfotree = ElementTree.parse(i_scenariorun.get("tripinfofile"))
                l_ettripinfos = l_ettripinfotree.getroot()
                l_vehicles = len(l_ettripinfos)
                for i_tripinfo in l_ettripinfos:
                    l_traveltimes.get(i_sortingmode).append(float(i_tripinfo.get("duration")))
                    l_timeloss.get(i_sortingmode).append(float(i_tripinfo.get("timeLoss")))


        self._visualisation.boxplot("Traveltime-{}_{}_vehicles_{}runs_one12segment.{}".format(
                                        p_scenarioname, l_vehicles, l_runs, "pdf"),
                                    "{}: Travel time for \n{} vehicles, {} runs for each mode, one 1+2 segment".format(
                                        p_scenarioname, l_vehicles, l_runs),
                                    l_traveltimes)

        self._visualisation.boxplot("TimeLoss-{}_{}_vehicles_{}runs_one12segment.{}".format(
            p_scenarioname, l_vehicles, l_runs, "pdf"),
            "{}: Time loss for \n{} vehicles, {} runs for each mode, one 1+2 segment".format(
                p_scenarioname, l_vehicles, l_runs),
            l_timeloss)


