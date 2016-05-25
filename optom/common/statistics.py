# -*- coding: utf-8 -*-
# @package statistics
# @cond LICENSE
# ######################################################################################
# # LGPL License                                                                       #
# #                                                                                    #
# # This file is part of the Optimisation of Overtaking Manoeuvres (OPTOM) project.                     #
# # Copyright (c) 2016, Malte Aschermann (malte.aschermann@tu-clausthal.de)            #
# # This program is free software: you can redistribute it and/or modify               #
# # it under the terms of the GNU Lesser General Public License as                     #
# # published by the Free Software Foundation, either version 3 of the                 #
# # License, or (at your option) any later version.                                    #
# #                                                                                    #
# # This program is distributed in the hope that it will be useful,                    #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of                     #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                      #
# # GNU Lesser General Public License for more details.                                #
# #                                                                                    #
# # You should have received a copy of the GNU Lesser General Public License           #
# # along with this program. If not, see http://www.gnu.org/licenses/                  #
# ######################################################################################
# @endcond
from __future__ import print_function
from __future__ import division
import log

try:
    from lxml import etree
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                except ImportError:
                    print("Failed to import ElementTree from any known place")


class Statistics(object):

    def __init__(self, p_args):
        self._log = log.logger(__name__, p_args.loglevel, p_args.logfile)

    def computeSUMOResults(self, p_scenarioname, p_scenarioruns, p_queries=[]):
        self._log.info("Traveltime statistics for scenario %s", p_scenarioname)

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

