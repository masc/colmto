# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

from configuration import Configuration
import xml.etree.ElementTree as ElementTree
from xml.dom import minidom
import os

class SumoConfig(object):

    def __init__(self, p_args):
        self._config = Configuration(p_args)
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
        l_runcfgsumo = self._config.getRunConfig().get("sumo")
        l_nodefile = l_runcfgsumo["nodefile"] = os.path.join(l_destinationdir, "{}.nod.xml".format(p_scenarioname))
        l_edgefile = l_runcfgsumo["edgefile"] = os.path.join(l_destinationdir, "{}.edg.xml".format(p_scenarioname))
        l_netfile = l_runcfgsumo["netfile"] = os.path.join(l_destinationdir, "{}.net.xml".format(p_scenarioname))
        l_routefile = l_runcfgsumo["routefile"] = os.path.join(l_destinationdir, "{}.rou.xml".format(p_scenarioname))
        l_settingsfile = l_runcfgsumo["settingsfile"] = os.path.join(l_destinationdir, "{}.settings.xml".format(p_scenarioname))
        l_configfile = l_runcfgsumo["configfile"] = os.path.join(l_destinationdir, "{}.config.cfg".format(p_scenarioname))

        self._generateNodeXML(p_roadwayconfig, l_nodefile)
        self._generateEdgeXML(p_roadwayconfig, l_edgefile)
        self._generateConfigXML(l_configfile, l_netfile, l_routefile, l_settingsfile,
                                l_runcfgsumo.get("time").get("begin"),
                                l_runcfgsumo.get("time").get("end"))
        self._generateSettingsXML(p_roadwayconfig, l_runcfgsumo.get("delay"), l_settingsfile)
        self._generateRouteXML(p_roadwayconfig, l_routefile)
        self._generateNetXML(p_roadwayconfig, l_netfile)

    ## Return a pretty-printed XML string for the Element (https://pymotw.com/2/xml/etree/ElementTree/create.html)
    def _prettify(self, p_element):
        return minidom.parseString(ElementTree.tostring(p_element)).toprettyxml(indent="  ")

    def _generateNodeXML(self, p_roadwayconfig, p_nodefile):

        # parameters
        l_length = p_roadwayconfig.get("parameters").get("length")

        l_nodes = ElementTree.Element("nodes")
        ElementTree.SubElement(l_nodes, "node", attrib={"id": "start", "x": "0", "y": "0"})
        ElementTree.SubElement(l_nodes, "node", attrib={"id": "end", "x": str(l_length), "y": "0"})

        with open(p_nodefile, "w") as fpnodesxml:
            fpnodesxml.write(self._prettify(l_nodes))

    def _generateEdgeXML(self, p_roadwayconfig, p_edgefile):

        # parameters
        l_length = p_roadwayconfig.get("parameters").get("length")
        l_switches = p_roadwayconfig.get("parameters").get("switches")

        # assume even distributed otl segment lengths
        l_segmentlength = l_length / ( l_switches + 1 )

        # create edges xml
        l_edges = ElementTree.Element("edges")
        l_edge = ElementTree.SubElement(l_edges, "edge", attrib={"id": "start-end", "from" : "start", "to": "end", "numLanes": "2"})

        # add splits and joins
        l_addotllane = False
        for i_segmentpos in xrange(0,int(l_length),int(l_segmentlength)):
            ElementTree.SubElement(l_edge, "split", attrib={"pos": str(i_segmentpos), "lanes": "0 1" if l_addotllane else "0"})
            l_addotllane ^= True

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

    def _generateRouteXML(self, p_roadwayconfig, p_routefile):
        l_aadt = p_roadwayconfig.get("parameters").get("aadt")
        l_vmax = p_roadwayconfig.get("parameters").get("vmax")
        l_type = p_roadwayconfig.get("parameters").get("type")


    def _generateSettingsXML(self, p_roadwayconfig, p_delay, p_settingsfile):

        l_viewsettings = ElementTree.Element("viewsettings")
        ElementTree.SubElement(l_viewsettings, "viewport",
                               attrib={"x": str(p_roadwayconfig.get("parameters").get("length") / 2),
                                       "y": "0",
                                       "zoom": "100"})
        ElementTree.SubElement(l_viewsettings, "delay", attrib={"value": str(p_delay)})

        with open(p_settingsfile, "w") as fpconfigxml:
            fpconfigxml.write(self._prettify(l_viewsettings))


    ## create net xml using netconvert
    def _generateNetXML(self, p_roadwayconfig, p_netfile):
        pass