# -*- coding: utf-8 -*-
# @package optom
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of Overtaking Manoeuvres project.   #
# # Copyright (c) 2016, Malte Aschermann (malte.aschermann@tu-clausthal.de)   #
# # This program is free software: you can redistribute it and/or modify      #
# # it under the terms of the GNU Lesser General Public License as            #
# # published by the Free Software Foundation, either version 3 of the        #
# # License, or (at your option) any later version.                           #
# #                                                                           #
# # This program is distributed in the hope that it will be useful,           #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# # GNU Lesser General Public License for more details.                       #
# #                                                                           #
# # You should have received a copy of the GNU Lesser General Public License  #
# # along with this program. If not, see http://www.gnu.org/licenses/         #
# #############################################################################
# @endcond
from __future__ import division
from __future__ import print_function

from collections import defaultdict
from collections import OrderedDict

import log
from io import Writer

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


s_iloop_template = etree.XML("""
    <xsl:stylesheet version= "1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
    <detector>
    <xsl:for-each select="detector/interval/typedInterval">
    <vehicle>
    <xsl:copy-of select="@id|@type|@begin"/>
    </vehicle>
    </xsl:for-each>
    </detector>
    </xsl:template>
    </xsl:stylesheet>""")


class Statistics(object):

    def __init__(self, p_args):
        self._log = log.logger(__name__, p_args.loglevel, p_args.logfile)
        self._writer = Writer(p_args)

    def compute_sumo_results(self, p_scenarioname, p_scenarioruns, p_iloopresults, p_deltas=("1_pre21-2_post21",
                                                                                             "1_pre21-3_exit",
                                                                                             "2_post21-3_exit")):
        self._log.info("Traveltime statistics for scenario %s", p_scenarioname)

        l_data = {
            "traveltime": {},
            "timeloss": {},
            "relativetimeloss": {}
        }

        l_runs = 0
        l_vehicles = 0

        for i_sortingmode, i_scenarioruns in p_scenarioruns.get("runs").iteritems():
            l_runs = len(i_scenarioruns)

            for i_run, i_scenariorun in i_scenarioruns.iteritems():
                l_tripfname = i_scenariorun.get("tripfile")
                l_ettripstree = etree.parse(l_tripfname)
                l_ettrips = l_ettripstree.getroot()
                l_trips = dict(map(lambda t: (t.attrib.get("id"), t.attrib), l_ettrips.iter("vType")))

                if l_vehicles == 0:
                    l_vehicles = len(p_iloopresults.get(i_sortingmode).get(i_run))

                for i_vid in l_trips:
                    l_vmaxspeed = l_trips.get(i_vid).get("maxSpeed")
                    l_label = "{}\n({} m/s)".format(i_sortingmode, str(int(float(l_vmaxspeed))).zfill(2))

                    for i_delta in p_deltas:
                        if l_data.get("traveltime").get(i_delta) is None:
                            l_data.get("traveltime")[i_delta] = {}
                        if l_data.get("traveltime").get(i_delta).get(l_label) is None:
                            l_data.get("traveltime").get(i_delta)[l_label] = []
                        l_data.get("traveltime").get(i_delta).get(l_label).append(
                            p_iloopresults.get(i_sortingmode).get(i_run).get(i_vid).get(i_delta)
                        )
                        if l_data.get("timeloss").get(i_delta) is None:
                            l_data.get("timeloss")[i_delta] = {}
                        if l_data.get("timeloss").get(i_delta).get(l_label) is None:
                            l_data.get("timeloss").get(i_delta)[l_label] = []
                        l_data.get("timeloss").get(i_delta).get(l_label).append(
                            p_iloopresults.get(i_sortingmode).get(i_run).get(i_vid).get(i_delta)
                        )

        return {
            "data": l_data,
            "nbvehicles": l_vehicles,
            "nbruns": l_runs
        }

    def traveltimes_from_iloops(self, p_runconfig, p_scenario):
        self._log.debug("Reading and aggregating induction loop logs")
        l_vehicles = p_runconfig.get("vehicles")
        l_total_length = p_scenario.get("parameters").get("length")
        l_nbswitches = p_scenario.get("parameters").get("switches")
        l_segmentlength = l_total_length / (l_nbswitches + 1)
        l_iloopfile = p_runconfig.get("iloopfile")
        l_root = etree.parse(l_iloopfile)
        l_iloop_detections = etree.XSLT(s_iloop_template)(l_root).iter("vehicle")
        # create a dictionary with vid -> detectorid -> timestep hierarchy for json output, for csv the same but flat
        l_vehicle_data_json = defaultdict(dict)
        l_vehicle_data_csv = []
        for i_v in l_iloop_detections:
            l_vehicle_data_json[i_v.get("type")][i_v.get("id")] = float(i_v.get("begin"))

        # calculate traveltimes and timeloss for each adjacent detector pair
        # a vehicle passed by using the recorded timestamp
        for i_vid, i_vdata in l_vehicle_data_json.iteritems():
            l_vehicle_speed_max = l_vehicles.get(i_vid).speed_max
            l_detectors = sorted(i_vdata.keys())

            l_vehicle_data_csv_row = OrderedDict({
                "vehicle": i_vid,
                "vtype": l_vehicles.get(i_vid).vtype,
                "speed_max": l_vehicle_speed_max
            })

            i_vdata["vtype"] = l_vehicles.get(i_vid).vtype
            i_vdata["speed_max"] = l_vehicle_speed_max

            for i_detector_x, i_detector_y in zip(l_detectors[:-1], l_detectors[1:]):
                l_traveltime = i_vdata.get(i_detector_y) - i_vdata.get(i_detector_x)
                l_detector_distance = p_scenario.get("detectorpositions").get(i_detector_y) - p_scenario.get("detectorpositions").get(i_detector_x)
                l_opt_travel_time = l_detector_distance / l_vehicle_speed_max
                l_timeloss = l_traveltime - l_opt_travel_time
                i_vdata["{}-{}".format(i_detector_x, i_detector_y)] = {
                    "distance": l_detector_distance,
                    "optimal_traveltime": l_opt_travel_time,
                    "travel_time": l_traveltime,
                    "time_loss": l_timeloss
                }
                l_vehicle_data_csv_row["{}-{}-distance".format(i_detector_x, i_detector_y)] = l_detector_distance
                l_vehicle_data_csv_row["{}-{}-optimal_traveltime".format(i_detector_x, i_detector_y)] = l_opt_travel_time
                l_vehicle_data_csv_row["{}-{}-travel_time".format(i_detector_x, i_detector_y)] = l_traveltime
                l_vehicle_data_csv_row["{}-{}-time_loss".format(i_detector_x, i_detector_y)] = l_timeloss

            l_vehicle_data_csv.append(l_vehicle_data_csv_row)

        return l_vehicle_data_json, l_vehicle_data_csv
