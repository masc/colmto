# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function

import os
import random
import subprocess
import xml.etree.ElementTree as ElementTree
from xml.dom import minidom
import itertools

from configuration import Configuration
from sumo.vehicle.vehicle import Vehicle

class SumoConfig(Configuration):

    def __init__(self, p_args, p_visualisation, p_netconvertbinary, p_duarouterbinary):
        super(SumoConfig, self).__init__(p_args)
        self._netconvertbinary = p_netconvertbinary
        self._duarouterbinary = p_duarouterbinary
        self._visualisation = p_visualisation
        self._forcerebuildscenarios = p_args.forcerebuildscenarios
        self._onlyoneotlsegment = p_args.onlyoneotlsegment
        self.generateAllSUMOConfigs()
        if p_args.headless == True:
            self.getRunConfig().get("sumo")["headless"] = True
        if p_args.gui == True:
            self.getRunConfig().get("sumo")["headless"] = False


    def get(self, p_key):
        return self.getRunConfig().get("sumo").get(p_key)

    def generateAllSUMOConfigs(self):
        map(lambda (name, cfg): self._generateSUMOConfig(name, cfg), self.getScenarioConfig().iteritems())

    def _generateSUMOConfig(self, p_scenarioname , p_scenarioconfig):

        l_destinationdir = os.path.join(self.getConfigDir(), "SUMO", p_scenarioname)
        if not os.path.exists(os.path.join(self.getConfigDir(), "SUMO")):
            os.mkdir(os.path.join(self.getConfigDir(), "SUMO"))
        if not os.path.exists(os.path.join(l_destinationdir)):
            os.mkdir(l_destinationdir)

        if self.getRunConfig().get("sumo") == None:
            self.getRunConfig()["sumo"] = {}

        if self.getRunConfig().get("sumo").get("scenarios") == None:
            self.getRunConfig().get("sumo")["scenarios"] = {}

        if self.getRunConfig().get("sumo").get("scenarios").get(p_scenarioname) == None:
            self.getRunConfig().get("sumo").get("scenarios")[p_scenarioname] = {}

        l_runcfg = self.getRunConfig()
        l_vtypescfg = self.getVtypesConfig()
        l_sumocfg = l_runcfg.get("sumo")
        l_scenarios = l_sumocfg.get("scenarios")
        l_nodefile = l_scenarios.get(p_scenarioname)["nodefile"] = os.path.join(l_destinationdir, "{}.nod.xml".format(p_scenarioname))
        l_edgefile = l_scenarios.get(p_scenarioname)["edgefile"] = os.path.join(l_destinationdir, "{}.edg.xml".format(p_scenarioname))
        l_netfile = l_scenarios.get(p_scenarioname)["netfile"] = os.path.join(l_destinationdir, "{}.net.xml".format(p_scenarioname))
        l_tripfile = l_scenarios.get(p_scenarioname)["tripfile"] = os.path.join(l_destinationdir, "{}.trip.xml".format(p_scenarioname))
        l_additionalfile = l_scenarios.get(p_scenarioname)["additionalfile"] = os.path.join(l_destinationdir, "{}.add.xml".format(p_scenarioname))
        l_routefile = l_scenarios.get(p_scenarioname)["routefile"] = os.path.join(l_destinationdir, "{}.rou.xml".format(p_scenarioname))
        l_settingsfile = l_scenarios.get(p_scenarioname)["settingsfile"] = os.path.join(l_destinationdir, "{}.settings.xml".format(p_scenarioname))
        l_configfile = l_scenarios.get(p_scenarioname)["configfile"] = os.path.join(l_destinationdir, "{}.config.cfg".format(p_scenarioname))
        l_scenarios.get(p_scenarioname)["tripinfofile"] = os.path.join(l_destinationdir, "{}.tripinfo.xml".format(p_scenarioname))
        l_sumocfgfiles = [l_nodefile, l_edgefile, l_netfile, l_tripfile, l_additionalfile, l_routefile, l_settingsfile, l_configfile]

        print(" * checking for SUMO configuration files for scenario", p_scenarioname)
        if len(filter(lambda fname: not os.path.isfile(fname), l_sumocfgfiles)) > 0:
            print("   incomplete scenario configuration detected -> forcing rebuild")
            self._forcerebuildscenarios = True

        self._generateNodeXML(p_scenarioconfig, l_nodefile, self._forcerebuildscenarios)
        self._generateEdgeXML(p_scenarioconfig, l_edgefile, self._forcerebuildscenarios)
        self._generateAdditionalXML(p_scenarioconfig, p_scenarioname, l_additionalfile, self._forcerebuildscenarios)
        self._generateConfigXML(l_configfile, l_netfile, l_routefile, l_additionalfile, l_settingsfile, l_runcfg.get("simtimeinterval"), self._forcerebuildscenarios)
        self._generateSettingsXML(p_scenarioconfig, l_runcfg, l_settingsfile, self._forcerebuildscenarios)
        self._generateTripXML(p_scenarioconfig, l_runcfg, l_vtypescfg, l_tripfile, self._forcerebuildscenarios)
        self._generateNetXML(l_nodefile, l_edgefile, l_netfile, self._forcerebuildscenarios)
        self._generateRouteXML(l_netfile, l_tripfile, l_routefile, self._forcerebuildscenarios)


    ## Return a pretty-printed XML string for the Element (https://pymotw.com/2/xml/etree/ElementTree/create.html)
    def _prettify(self, p_element):
        return minidom.parseString(ElementTree.tostring(p_element)).toprettyxml(indent="  ")

    def _generateNodeXML(self, p_scenarioconfig, p_nodefile, p_forcerebuildscenarios=False):
        if os.path.isfile(p_nodefile) and not p_forcerebuildscenarios:
            return

        # parameters
        l_length = p_scenarioconfig.get("parameters").get("length")
        l_nbswitches = p_scenarioconfig.get("parameters").get("switches")

        if self._onlyoneotlsegment:
            l_length = 2*(l_length / (l_nbswitches+1)) # two times segment length

        l_nodes = ElementTree.Element("nodes")
        #ElementTree.SubElement(l_nodes, "node", attrib={"id": "ramp_start", "x": "-1500", "y": "0"})
        ElementTree.SubElement(l_nodes, "node", attrib={"id": "2_1_start", "x": "0", "y": "0"})
        ElementTree.SubElement(l_nodes, "node", attrib={"id": "2_1_end", "x": str(l_length), "y": "0"})
        # dummy node for easier from-to routing
        l_segmentlength = l_length / ( l_nbswitches + 1 )
        ElementTree.SubElement(l_nodes, "node", attrib={"id": "ramp_exit", "x": str(l_length+l_segmentlength), "y": "0"})

        with open(p_nodefile, "w") as fpnodesxml:
            fpnodesxml.write(self._prettify(l_nodes))

    def _generateEdgeXML(self, p_scenarioconfig, p_edgefile, p_forcerebuildscenarios=False):
        if os.path.isfile(p_edgefile) and not p_forcerebuildscenarios:
            return

        # parameters
        l_length = p_scenarioconfig.get("parameters").get("length")
        l_nbswitches = p_scenarioconfig.get("parameters").get("switches")
        l_maxspeed = p_scenarioconfig.get("parameters").get("maxSpeed")

        # assume even distributed otl segment lengths
        l_segmentlength = l_length / ( l_nbswitches + 1 )

        # create edges xml
        l_edges = ElementTree.Element("edges")
        l_21edge = ElementTree.SubElement(l_edges, "edge", attrib={"id": "2_1_segment",
                                                                   "from" : "2_1_start",
                                                                   "to": "2_1_end",
                                                                   "numLanes": "2",
                                                                   "speed": str(l_maxspeed)})

        # add splits and joins
        l_addotllane = False
        for i_segmentpos in xrange(0,int(l_length),int(l_segmentlength)) \
                if not self._onlyoneotlsegment else xrange(0,int(2*l_segmentlength),int(l_segmentlength)):
            ElementTree.SubElement(l_21edge, "split", attrib={"pos": str(i_segmentpos),
                                                              "lanes": "0 1" if l_addotllane else "0",
                                                              "speed": str(l_maxspeed)})
            l_addotllane ^= True

        # dummy edge
        ElementTree.SubElement(l_edges, "edge", attrib={"id": "2_1_end-ramp_exit",
                                                        "from" : "2_1_end",
                                                        "to": "ramp_exit",
                                                        "numLanes": "1",
                                                        "speed": str(l_maxspeed)})

        with open(p_edgefile, "w") as fpedgexml:
            fpedgexml.write(self._prettify(l_edges))

    def _generateAdditionalXML(self, p_scenarioconfig, p_scenarioname, p_additionalfile, p_forcerebuildscenarios):
        if os.path.isfile(p_additionalfile) and not p_forcerebuildscenarios:
            return

        # parameters
        l_length = p_scenarioconfig.get("parameters").get("length")
        l_nbswitches = p_scenarioconfig.get("parameters").get("switches")

        # assume even distributed otl segment lengths
        l_segmentlength = l_length / ( l_nbswitches + 1 )

        l_additional = ElementTree.Element("additional")
        # place induction loop right before the first split (i.e. end of starting edge)
        #     <inductionLoop id="myLoop1" lane="foo_0" pos="42" freq="900" file="out.xml"/>
        ElementTree.SubElement(l_additional, "inductionLoop",
                               attrib={
                                   "id": "start",
                                   "lane": "2_1_segment_0",
                                   "pos": str(l_segmentlength),
                                   "friendlyPos": "true",
                                   "freq" : "900",
                                   "file": os.path.join(self.getConfigDir(),"SUMO", p_scenarioname, "{}.inductionLoop.start.xml".format(p_scenarioname))
                               })

        ElementTree.SubElement(l_additional, "inductionLoop",
                               attrib={
                                   "id": "exit",
                                   "lane": "2_1_end-ramp_exit_0",
                                   "pos": str(l_segmentlength),
                                   "friendlyPos": "true",
                                   "freq" : "900",
                                   "file": os.path.join(self.getConfigDir(),"SUMO", p_scenarioname, "{}.inductionLoop.exit.xml".format(p_scenarioname))
                               })
        with open(p_additionalfile, "w") as fpaddxml:
            fpaddxml.write(self._prettify(l_additional))

    ## create sumo config
    def _generateConfigXML(self, p_configfile, p_netfile, p_routefile, p_additionalfile, p_settingsfile, p_simtimeinterval, p_forcerebuildscenarios=False):
        if os.path.isfile(p_configfile) and not p_forcerebuildscenarios:
            return
        assert type(p_simtimeinterval) == list and len(p_simtimeinterval) == 2

        l_configuration = ElementTree.Element("configuration")
        l_input = ElementTree.SubElement(l_configuration, "input")
        ElementTree.SubElement(l_input, "net-file", attrib={"value": p_netfile})
        ElementTree.SubElement(l_input, "route-files", attrib={"value": p_routefile})
        ElementTree.SubElement(l_input, "additional-files", attrib={"value": p_additionalfile})
        ElementTree.SubElement(l_input, "gui-settings-file", attrib={"value": p_settingsfile})
        l_time = ElementTree.SubElement(l_configuration, "time")
        ElementTree.SubElement(l_time, "begin", attrib={"value": str(p_simtimeinterval[0])})
        ElementTree.SubElement(l_time, "end", attrib={"value": str(p_simtimeinterval[1])})

        with open(p_configfile, "w") as fpconfigxml:
            fpconfigxml.write(self._prettify(l_configuration))

    def _generateSettingsXML(self, p_scenarioconfig, p_runcfg, p_settingsfile, p_forcerebuildscenarios=False):
        if os.path.isfile(p_settingsfile) and not p_forcerebuildscenarios:
            return

        l_viewsettings = ElementTree.Element("viewsettings")
        ElementTree.SubElement(l_viewsettings, "viewport",
                               attrib={"x": str(p_scenarioconfig.get("parameters").get("length") / 2),
                                       "y": "0",
                                       "zoom": "100"})
        ElementTree.SubElement(l_viewsettings, "delay", attrib={"value": str(p_runcfg.get("sumo").get("gui-delay"))})

        with open(p_settingsfile, "w") as fpconfigxml:
            fpconfigxml.write(self._prettify(l_viewsettings))

    def _nextTime(self, p_lambda, p_prevstarttime, p_distribution="poisson"):
        if p_distribution=="poisson":
            return p_prevstarttime+random.expovariate(p_lambda)
        elif p_distribution=="linear":
            return p_prevstarttime+1/p_lambda
        else:
            return p_prevstarttime

    def _createFixedInitialVehicleDistribution(self, p_vtypescfg, p_runcfg, p_scenarioconfig, p_nbvehicles, p_aadt, p_initialsorting, p_vtypedistribution):
        print("create fixed initial vehicle distribution with {}".format(p_vtypedistribution))
        l_vtypedistribution = list(itertools.chain.from_iterable(
            map(
                lambda (k,v): [k] * int(round(100 * v.get("fraction"))),
                p_vtypedistribution.iteritems()
            )
        ))

        l_vehps = p_aadt / (24*60*60) \
            if not p_runcfg.get("vehiclespersecond").get("enabled") else p_runcfg.get("vehiclespersecond").get("value")

        l_vehicles = map(
            lambda vtype: Vehicle(p_vtypescfg.get(vtype), p_vtypedistribution.get(vtype).get("speedsigma")),
            [random.choice(l_vtypedistribution) for i in xrange(p_nbvehicles)]
        )

        # generate color map for vehicle max speeds
        l_colormap = self._visualisation.getColormap(
            xrange(int(round(p_scenarioconfig.get("parameters").get("maxSpeed")))),
            'jet_r'
        )

        # update colors
        for i_vehicle in l_vehicles:
            i_vehicle.setColor(l_colormap.to_rgba(i_vehicle.getMaxSpeed()))

        # sort speeds according to initialsorting flag
        if p_initialsorting == "bestcase":
            l_vehicles.sort(key=lambda v: v.getMaxSpeed(), reverse=True)
        elif p_initialsorting == "worstcase":
            l_vehicles.sort(key=lambda v: v.getMaxSpeed())

        # assign start time and id to each vehicle
        for i,i_vehicle in enumerate(l_vehicles):
            i_vehicle.provision("vehicle{}".format(i),
                                self._nextTime(l_vehps,
                                               l_vehicles[i-1].getStartTime() if i > 0 else 0,
                                               p_runcfg.get("starttimedistribution")))

        return l_vehicles



    def _generateTripXML(self, p_scenarioconfig, p_runcfg, p_vtypescfg, p_tripfile, p_forcerebuildscenarios=False):
        if os.path.isfile(p_tripfile) and not p_forcerebuildscenarios:
            return

        # generate simple traffic demand by considering AADT, Vmax, roadtype etc
        l_aadt = p_scenarioconfig.get("parameters").get("aadt") \
            if not p_runcfg.get("aadt").get("enabled") else p_runcfg.get("aadt").get("value")

        l_timebegin, l_timeend = p_runcfg.get("simtimeinterval")

        # number of vehicles = AADT / [seconds of day] * [scenario time in seconds]
        l_numberofvehicles = int(round(l_aadt / (24*60*60) * (l_timeend - l_timebegin))) \
            if not p_runcfg.get("nbvehicles").get("enabled") else p_runcfg.get("nbvehicles").get("value")

        print("Scenario's AADT of {} vehicles/average annual day => {} vehicles for {} simulation seconds".format(
            l_aadt, l_numberofvehicles, (l_timeend - l_timebegin)
        ))

        l_vehicles = self._createFixedInitialVehicleDistribution(p_vtypescfg,
                                                                 p_runcfg,
                                                                 p_scenarioconfig,
                                                                 l_numberofvehicles,
                                                                 l_aadt,
                                                                 p_runcfg.get("initialsorting"),
                                                                 p_runcfg.get("vtypedistribution")
                                                                 )


        # xml
        l_trips = ElementTree.Element("trips")

        # create a sumo vtype for each desired speed
        l_vtypes = dict(map(lambda v: (int(v.getMaxSpeed()), v), l_vehicles))

        for i_vtype, i_vehicle in l_vtypes.iteritems():

            # filter for relevant attributes
            l_vattr = dict( map( lambda (k, v): (k, str(v)), filter(
                lambda (k, v): k in ["vClass","length","width","height","minGap","accel","decel","speedFactor","speedDev"], i_vehicle.getVType().iteritems()
            )))
            l_vattr["id"] = str(i_vtype)
            l_vattr["type"] = l_vattr.get("vClass")
            l_vattr["maxSpeed"] = str(i_vehicle.getMaxSpeed())
            ElementTree.SubElement(l_trips, "vType", attrib=l_vattr)

        # add trips
        for i_vehicle in l_vehicles:
            ElementTree.SubElement(l_trips, "trip", attrib={
                "id": i_vehicle.getID(),
                "depart": str(i_vehicle.getStartTime()),
                "from": "2_1_segment",
                "to": "2_1_end-ramp_exit",
                "type": str(i_vehicle.getMaxSpeed()),
                "departSpeed": "max",
                "color" : "{},{},{},{}".format(*i_vehicle.getColor())
            })

        with open(p_tripfile, "w") as fptripxml:
            fptripxml.write(self._prettify(l_trips))

    ## create net xml using netconvert
    def _generateNetXML(self, p_nodefile, p_edgefile, p_netfile, p_forcerebuildscenarios=False):
        if os.path.isfile(p_netfile) and not p_forcerebuildscenarios:
            return

        l_netconvertprocess = subprocess.Popen([self._netconvertbinary,
                                               "--node-files={}".format(p_nodefile),
                                               "--edge-files={}".format(p_edgefile),
                                               "--output-file={}".format(p_netfile)])
        l_netconvertprocess.wait()

    def _generateRouteXML(self, p_netfile, p_tripfile, p_routefile, p_forcerebuildscenarios=False):
        if os.path.isfile(p_routefile) and not p_forcerebuildscenarios:
            return

        l_duarouterprocess = subprocess.Popen([self._duarouterbinary,
                                                "-n", p_netfile,
                                                "-t", p_tripfile,
                                                "-o", p_routefile])
        l_duarouterprocess.wait()

