# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import xml.etree.ElementTree as ElementTree
from visualisation import Visualisation

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

        l_traveltimes = {}

        l_runs = 0
        l_vehicles = 0
        for i_sortingmode, i_scenarioruns in p_scenarioruns.iteritems():
            l_runs = len(i_scenarioruns)
            for i_run, i_scenariorun in i_scenarioruns.iteritems():
                l_ettripstree = ElementTree.parse(i_scenariorun.get("tripfile"))
                l_ettrips = l_ettripstree.getroot()
                l_trips = dict(map(lambda t: (t.attrib.get("id"), t.attrib), l_ettrips.iter("vType")))

                l_ettripinfotree = ElementTree.parse(i_scenariorun.get("tripinfofile"))
                l_ettripinfos = l_ettripinfotree.getroot()
                l_vehicles = len(l_ettripinfos)

                for i_tripinfo in l_ettripinfos:
                    l_vid = i_tripinfo.get("id")
                    l_vmaxspeed = l_trips.get(l_vid).get("maxSpeed")
                    l_label = "{} ({} m/s)".format(i_sortingmode, l_vmaxspeed)
                    if l_traveltimes.get(l_label) is None:
                        l_traveltimes[l_label] = []

                    l_traveltimes.get(l_label).append(float(i_tripinfo.get("duration")))

        return { "data": l_traveltimes, "nbvehicles": l_vehicles, "nbruns": l_runs }

    def timeloss(self, p_scenarioname, p_scenarioruns):
        print("* time loss statistics for scenario {}".format(p_scenarioname))

        l_timeloss = {}

        l_runs = 0
        l_vehicles = 0
        for i_sortingmode, i_scenarioruns in p_scenarioruns.iteritems():
            l_runs = len(i_scenarioruns)
            for i_run, i_scenariorun in i_scenarioruns.iteritems():
                l_ettripstree = ElementTree.parse(i_scenariorun.get("tripfile"))
                l_ettrips = l_ettripstree.getroot()
                l_trips = dict(map(lambda t: (t.attrib.get("id"), t.attrib), l_ettrips.iter("vType")))

                l_ettripinfotree = ElementTree.parse(i_scenariorun.get("tripinfofile"))
                l_ettripinfos = l_ettripinfotree.getroot()
                l_vehicles = len(l_ettripinfos)

                for i_tripinfo in l_ettripinfos:
                    l_vid = i_tripinfo.get("id")
                    l_vmaxspeed = l_trips.get(l_vid).get("maxSpeed")
                    l_label = "{} ({} m/s)".format(i_sortingmode, l_vmaxspeed)
                    if l_timeloss.get(l_label) is None:
                        l_timeloss[l_label] = []

                    l_timeloss.get(l_label).append(float(i_tripinfo.get("timeLoss")))

        return { "data": l_timeloss, "nbvehicles": l_vehicles, "nbruns": l_runs }
