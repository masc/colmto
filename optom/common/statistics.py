# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

try:
    from lxml import etree
    print("running with lxml.etree")
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
        print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
            print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
                print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                    print("running with ElementTree")
                except ImportError:
                    print("Failed to import ElementTree from any known place")


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



    def computeSUMOResults(self, p_scenarioname, p_scenarioruns, p_queries=[]):
        print("* traveltime statistics for scenario {}".format(p_scenarioname))

        l_data = dict([(q, {}) for q in p_queries])
        l_data["relativeLoss"] = {}
        l_runs = 0
        l_vehicles = 0

        for i_sortingmode, i_scenarioruns in p_scenarioruns.get("runs").iteritems():
            l_runs = len(i_scenarioruns)

            for i_run, i_scenariorun in i_scenarioruns.iteritems():
                l_tripfname = i_scenariorun.get("tripfile")
                l_ettripstree = etree.parse(l_tripfname)
                l_ettrips = l_ettripstree.getroot()
                l_trips = dict(map(lambda t: (t.attrib.get("id"), t.attrib), l_ettrips.iter("vType")))

                l_tripinfofname = i_scenariorun.get("tripinfofile")
                l_ettripinfotree = etree.parse(l_tripinfofname)
                l_ettripinfos = l_ettripinfotree.getroot()
                l_vehicles = len(l_ettripinfos)

                for i_tripinfo in l_ettripinfos:
                    l_vid = i_tripinfo.get("id")
                    l_vmaxspeed = l_trips.get(l_vid).get("maxSpeed")
                    l_label = "{}\n({} m/s)".format(i_sortingmode, str(int(float(l_vmaxspeed))).zfill(2))

                    for i_query in p_queries:
                        if l_data.get(i_query).get(l_label) is None:
                            l_data.get(i_query)[l_label] = []
                        l_data.get(i_query).get(l_label).append(float(i_tripinfo.get(i_query)))
                    # hack for relative time loss
                    l_traveltime = float(i_tripinfo.get("duration"))
                    l_timeloss = float(i_tripinfo.get("timeLoss"))
                    l_topt = l_traveltime - l_timeloss
                    l_relativeloss = l_timeloss / l_topt * 100.
                    if l_data.get("relativeLoss").get(l_label) is None:
                        l_data.get("relativeLoss")[l_label] = []
                    l_data.get("relativeLoss").get(l_label).append(l_relativeloss)


        return {
            "data": l_data,
            "nbvehicles": l_vehicles,
            "nbruns": l_runs
        }

