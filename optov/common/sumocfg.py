# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

from configuration import Configuration
import xml.etree.ElementTree as ElementTree
from xml.dom import minidom
import random
import subprocess
import os
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.pyplot as plt

class SumoConfig(object):

    def __init__(self, p_args, p_netconvertbinary, p_duarouterbinary):
        self._config = Configuration(p_args)
        self._netconvertbinary = p_netconvertbinary
        self._duarouterbinary = p_duarouterbinary
        self.generateSUMOConfigs()


    def getConfig(self):
        return self._config

    def generateSUMOConfigs(self):
        map(lambda (name, cfg): self._generateSUMOConfig(name, cfg), self._config.getRoadwayConfig().iteritems())

    def _generateSUMOConfig(self, p_scenarioname , p_roadwayconfig):

        print("generating SUMO configuration files for scenario", p_scenarioname)

        l_destinationdir = os.path.join(self._config.getConfigDir(), "SUMO", p_scenarioname)
        if not os.path.exists(os.path.join(self._config.getConfigDir(), "SUMO")):
            os.mkdir(os.path.join(self._config.getConfigDir(), "SUMO"))
        if not os.path.exists(os.path.join(l_destinationdir)):
            os.mkdir(l_destinationdir)

        if self._config.getRunConfig().get("sumo") == None:
            self._config.getRunConfig()["sumo"] = {}
        l_runcfg = self._config.getRunConfig()
        l_nodefile = l_runcfg.get("sumo")["nodefile"] = os.path.join(l_destinationdir, "{}.nod.xml".format(p_scenarioname))
        l_edgefile = l_runcfg.get("sumo")["edgefile"] = os.path.join(l_destinationdir, "{}.edg.xml".format(p_scenarioname))
        l_netfile = l_runcfg.get("sumo")["netfile"] = os.path.join(l_destinationdir, "{}.net.xml".format(p_scenarioname))
        l_tripfile = l_runcfg.get("sumo")["tripfile"] = os.path.join(l_destinationdir, "{}.trip.xml".format(p_scenarioname))
        l_routefile = l_runcfg.get("sumo")["routefile"] = os.path.join(l_destinationdir, "{}.rou.xml".format(p_scenarioname))
        l_settingsfile = l_runcfg.get("sumo")["settingsfile"] = os.path.join(l_destinationdir, "{}.settings.xml".format(p_scenarioname))
        l_configfile = l_runcfg.get("sumo")["configfile"] = os.path.join(l_destinationdir, "{}.config.cfg".format(p_scenarioname))

        self._generateNodeXML(p_roadwayconfig, l_nodefile)
        self._generateEdgeXML(p_roadwayconfig, l_edgefile)
        self._generateConfigXML(l_configfile, l_netfile, l_routefile, l_settingsfile,
                                l_runcfg.get("sumo").get("time").get("begin"),
                                l_runcfg.get("sumo").get("time").get("end"))
        self._generateSettingsXML(p_roadwayconfig, l_runcfg, l_settingsfile)
        self._generateTripXML(p_roadwayconfig, l_runcfg, l_tripfile)
        self._generateNetXML(l_nodefile, l_edgefile, l_netfile)
        self._generateRouteXML(l_netfile, l_tripfile, l_routefile)

    ## Return a pretty-printed XML string for the Element (https://pymotw.com/2/xml/etree/ElementTree/create.html)
    def _prettify(self, p_element):
        return minidom.parseString(ElementTree.tostring(p_element)).toprettyxml(indent="  ")

    def _generateNodeXML(self, p_roadwayconfig, p_nodefile):

        # parameters
        l_length = p_roadwayconfig.get("parameters").get("length")

        l_nodes = ElementTree.Element("nodes")
        #ElementTree.SubElement(l_nodes, "node", attrib={"id": "ramp_entrance", "x": "-500", "y": "0"})
        ElementTree.SubElement(l_nodes, "node", attrib={"id": "2_1_start", "x": "0", "y": "0"})
        ElementTree.SubElement(l_nodes, "node", attrib={"id": "2_1_end", "x": str(l_length), "y": "0"})
        ElementTree.SubElement(l_nodes, "node", attrib={"id": "ramp_exit", "x": str(l_length+0.1), "y": "0"})

        with open(p_nodefile, "w") as fpnodesxml:
            fpnodesxml.write(self._prettify(l_nodes))

    def _generateEdgeXML(self, p_roadwayconfig, p_edgefile):

        # parameters
        l_length = p_roadwayconfig.get("parameters").get("length")
        l_switches = p_roadwayconfig.get("parameters").get("switches")
        l_maxspeed = p_roadwayconfig.get("parameters").get("maxSpeed")

        # assume even distributed otl segment lengths
        l_segmentlength = l_length / ( l_switches + 1 )

        # create edges xml
        l_edges = ElementTree.Element("edges")
        #ElementTree.SubElement(l_edges, "edge", attrib={"id": "ramp_entrance-2_1_start", "from" : "ramp_entrance", "to": "2_1_start", "numLanes": "1"})
        l_21edge = ElementTree.SubElement(l_edges, "edge", attrib={"id": "2_1_segment",
                                                                   "from" : "2_1_start",
                                                                   "to": "2_1_end",
                                                                   "numLanes": "2",
                                                                   "speed": str(l_maxspeed)})

        # add splits and joins
        l_addotllane = False
        for i_segmentpos in xrange(0,int(l_length),int(l_segmentlength)):
            ElementTree.SubElement(l_21edge, "split", attrib={"pos": str(i_segmentpos),
                                                              "lanes": "0 1" if l_addotllane else "0",
                                                              "speed": str(l_maxspeed)})
            l_addotllane ^= True

        ElementTree.SubElement(l_edges, "edge", attrib={"id": "2_1_end-ramp_exit",
                                                        "from" : "2_1_end",
                                                        "to": "ramp_exit",
                                                        "numLanes": "2" if l_addotllane else "1",
                                                        "speed": str(l_maxspeed)})

        with open(p_edgefile, "w") as fpedgexml:
            fpedgexml.write(self._prettify(l_edges))


    ## create sumo config
    def _generateConfigXML(self, p_configfile, p_netfile, p_routefile, p_settingsfile, p_begin, p_end):

        l_configuration = ElementTree.Element("configuration")
        l_input = ElementTree.SubElement(l_configuration, "input")
        ElementTree.SubElement(l_input, "net-file", attrib={"value": p_netfile})
        ElementTree.SubElement(l_input, "route-files", attrib={"value": p_routefile})
        ElementTree.SubElement(l_input, "gui-settings-file", attrib={"value": p_settingsfile})
        l_time = ElementTree.SubElement(l_configuration, "time")
        ElementTree.SubElement(l_time, "begin", attrib={"value": str(p_begin)})
        ElementTree.SubElement(l_time, "end", attrib={"value": str(p_end)})

        with open(p_configfile, "w") as fpconfigxml:
            fpconfigxml.write(self._prettify(l_configuration))

    def _generateSettingsXML(self, p_roadwayconfig, p_runcfg, p_settingsfile):

        l_viewsettings = ElementTree.Element("viewsettings")
        ElementTree.SubElement(l_viewsettings, "viewport",
                               attrib={"x": str(p_roadwayconfig.get("parameters").get("length") / 2),
                                       "y": "0",
                                       "zoom": "100"})
        ElementTree.SubElement(l_viewsettings, "delay", attrib={"value": str(p_runcfg.get("sumo").get("gui-delay"))})

        with open(p_settingsfile, "w") as fpconfigxml:
            fpconfigxml.write(self._prettify(l_viewsettings))

    def _createVehicleDistribution(self, p_distribution, p_args, p_nbvehicles, p_aadt):
        l_speeddistribution = []
        l_starttimes = []
        while len(l_speeddistribution) < p_nbvehicles:
            l_vid = len(l_speeddistribution)
            if p_distribution == "GAUSS":
                l_dspeed = int(round(random.gauss(*p_args)))
            else:
                l_dspeed = 250
            if l_dspeed > 0:
                l_vehps = (p_aadt / (24*60*60))
                l_starttimes.append(int((l_vid+1) / l_vehps))
                l_speeddistribution.append(l_dspeed)


        return l_speeddistribution, l_starttimes

    def _getColormap(self, p_desiredspeeds):
        l_jet=plt.get_cmap('jet_r')
        l_cnorm  = colors.Normalize(vmin=min(p_desiredspeeds), vmax=max(p_desiredspeeds))
        return cm.ScalarMappable(norm=l_cnorm, cmap=l_jet)

    def _generateTripXML(self, p_roadwayconfig, p_runcfg, p_tripfile):
        # generate simple traffic demand by considering AADT, Vmax, roadtype etc
        l_aadt = p_roadwayconfig.get("parameters").get("aadt")
        l_timebegin = p_runcfg.get("sumo").get("time").get("begin")
        l_timeend = p_runcfg.get("sumo").get("time").get("end")

        # number of vehicles = AADT / [seconds of day] * [scenario time in seconds]
        l_numberofvehicles = int(round(l_aadt / (24 * 3600) * (l_timeend - l_timebegin)))
        print("Scenaro's AADT of {} vehicles/average annual day => {} vehicles for {} simulation seconds".format(
            l_aadt, l_numberofvehicles, (l_timeend - l_timebegin)
        ))
        l_dspeeddistribution, l_starttimes = self._createVehicleDistribution(
            p_runcfg.get("desiredspeeds").get("distribution"),
            p_runcfg.get("desiredspeeds").get("args"),
            l_numberofvehicles,
            l_aadt
        )

        # generate colormap for speeds
        l_colormap = self._getColormap(l_dspeeddistribution)

        # create unique vtypes identified by dspeed
        l_vtypeset = list(set(l_dspeeddistribution))

        # xml
        l_trips = ElementTree.Element("trips")

        # create vehicles as dictionaries containing the type depending on desired speed buckets (see cfg)
        for i_dspeed in l_vtypeset:
            l_vid, l_vattr = filter(
                lambda (k, v): v.get("dspeedbucket").get("min") <= i_dspeed < v.get("dspeedbucket").get("max"),
                p_runcfg.get("vtypes").iteritems()
            ).pop()
            # filter for relevant attributes
            l_vattr = dict( map( lambda (k, v): (k, str(v)), filter(
                lambda (k, v): k in ["length","width","height","minGap","accel","decel","speedFactor","speedDev"], l_vattr.iteritems()
            )))
            l_vattr["id"] = str(i_dspeed)
            l_vattr["type"] = l_vid
            l_vattr["maxSpeed"] = str(i_dspeed)
            l_vattr["color"] = "{},{},{},{}".format(*l_colormap.to_rgba(i_dspeed))
            ElementTree.SubElement(l_trips, "vType", attrib=l_vattr)

        # add trips
        map(lambda (i_id, i_dspeed):
            ElementTree.SubElement(l_trips, "trip", attrib={
                "id": str(i_id), "depart": str(l_starttimes[i_id]), "from": "2_1_segment", "to": "2_1_end-ramp_exit", "type": str(i_dspeed), "departSpeed": "max"
            }), enumerate(l_dspeeddistribution))

        with open(p_tripfile, "w") as fptripxml:
            fptripxml.write(self._prettify(l_trips))

    ## create net xml using netconvert
    def _generateNetXML(self, p_nodefile, p_edgefile, p_netfile):
        l_netconvertprocess = subprocess.Popen([self._netconvertbinary,
                                               "--node-files={}".format(p_nodefile),
                                               "--edge-files={}".format(p_edgefile),
                                               "--output-file={}".format(p_netfile)])
        l_netconvertprocess.wait()

    def _generateRouteXML(self, p_netfile, p_tripfile, p_routefile):
        l_duarouterprocess = subprocess.Popen([self._duarouterbinary,
                                                "-n", p_netfile,
                                                "-t", p_tripfile,
                                                "-o", p_routefile])
        l_duarouterprocess.wait()

