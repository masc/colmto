# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function

import os
import random
import subprocess
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
        self._sumoconfigdir = os.path.join(self.getConfigDir(), "SUMO")
        if not os.path.exists(self._sumoconfigdir):
            os.mkdir(self._sumoconfigdir)

        if self._forcerebuildscenarios:
            print(" * forcerebuildscenarios set -> rebuilding/overwriting scenarios if already present")
        self._onlyoneotlsegment = p_args.onlyoneotlsegment


    def getSUMOConfigDir(self):
        return self._sumoconfigdir

    def get(self, p_key):
        return self.getRunConfig().get("sumo").get(p_key)

    def generateScenario(self, p_scenarioname):
        l_destinationdir = os.path.join(self.getSUMOConfigDir(), p_scenarioname)
        if not os.path.exists(os.path.join(l_destinationdir)):
            os.mkdir(l_destinationdir)

        l_scenarioconfig = self.getScenarioConfig().get(p_scenarioname)
        l_runcfg = self.getRunConfig()

        l_scenarioruns = {
            "scenarioname": p_scenarioname,
            "runs": {}
        }

        l_nodefile = l_scenarioruns["nodefile"] = os.path.join(l_destinationdir, "{}.nod.xml".format(p_scenarioname))
        l_edgefile = l_scenarioruns["edgefile"] = os.path.join(l_destinationdir, "{}.edg.xml".format(p_scenarioname))
        l_netfile = l_scenarioruns["netfile"] = os.path.join(l_destinationdir, "{}.net.xml".format(p_scenarioname))
        l_settingsfile = l_scenarioruns["settingsfile"] = os.path.join(l_destinationdir, "{}.settings.xml".format(p_scenarioname))

        self._generateNodeXML(l_scenarioconfig, l_nodefile, self._forcerebuildscenarios)
        self._generateEdgeXML(l_scenarioconfig, l_edgefile, self._forcerebuildscenarios)
        self._generateSettingsXML(l_scenarioconfig, l_runcfg, l_settingsfile, self._forcerebuildscenarios)
        self._generateNetXML(l_nodefile, l_edgefile, l_netfile, self._forcerebuildscenarios)

        return l_scenarioruns

    def generateRun(self, p_scenarioruns, p_initialsorting, p_run):
        l_scenarioname = p_scenarioruns.get("scenarioname")
        l_scenarioconfig = self.getScenarioConfig().get(l_scenarioname)

        l_destinationdir = os.path.join(self.getSUMOConfigDir(), p_scenarioruns.get("scenarioname"))
        if not os.path.exists(os.path.join(l_destinationdir)):
            os.mkdir(l_destinationdir)

        l_runcfg = self.getRunConfig()

        l_vtypescfg = self.getVtypesConfig()

        if not os.path.exists(os.path.join(l_destinationdir, str(p_initialsorting))):
            os.mkdir(os.path.join(os.path.join(l_destinationdir, str(p_initialsorting))))

        if not os.path.exists(os.path.join(l_destinationdir, str(p_initialsorting), str(p_run))):
            os.mkdir(os.path.join(os.path.join(l_destinationdir, str(p_initialsorting), str(p_run))))

        print(" * generating SUMO run configuration for scenario {} / sorting {} / run {}".format(l_scenarioname, p_initialsorting, p_run))
        if p_scenarioruns.get("runs").get(p_initialsorting) is None:
            p_scenarioruns.get("runs")[p_initialsorting] = {}
        p_scenarioruns.get("runs").get(p_initialsorting)[p_run] = {}
        l_scenariorun = p_scenarioruns.get("runs").get(p_initialsorting).get(p_run)

        l_netfile = p_scenarioruns.get("netfile")
        l_settingsfile = p_scenarioruns.get("settingsfile")

        l_additionalfile = l_scenariorun["additionalfile"] = os.path.join(l_destinationdir, str(p_initialsorting), str(p_run), "{}.add.xml".format(l_scenarioname))
        l_tripfile = l_scenariorun["tripfile"] = os.path.join(l_destinationdir, str(p_initialsorting), str(p_run), "{}.trip.xml".format(l_scenarioname))
        l_routefile = l_scenariorun["routefile"] = os.path.join(l_destinationdir, str(p_initialsorting), str(p_run), "{}.rou.xml".format(l_scenarioname))
        l_configfile = l_scenariorun["configfile"] = os.path.join(l_destinationdir, str(p_initialsorting), str(p_run), "{}.sumo.cfg".format(l_scenarioname))
        l_tripinfofile = l_scenariorun["tripinfofile"] = os.path.join(l_destinationdir, str(p_initialsorting), str(p_run), "{}.tripinfo-output.xml".format(l_scenarioname))
        l_fcdfile = l_scenariorun["fcdfile"] = os.path.join(l_destinationdir, str(p_initialsorting), str(p_run), "{}.fcd-output.xml".format(l_scenarioname))

        l_runcfgfiles = [l_tripfile, l_additionalfile, l_routefile, l_configfile]

        if len(filter(lambda fname: not os.path.isfile(fname), l_runcfgfiles)) > 0:
            print("   not existing or incomplete scenario configuration detected -> rebuilding")
            self._forcerebuildscenarios = True

        self._generateAdditionalXML(l_scenarioconfig, p_initialsorting, p_run, l_scenarioname, l_additionalfile, self._forcerebuildscenarios)
        self._generateConfigXML(l_configfile, l_netfile, l_routefile, l_additionalfile, l_settingsfile, l_runcfg.get("simtimeinterval"), self._forcerebuildscenarios)
        self._generateTripXML(l_scenarioconfig, l_runcfg, p_initialsorting, l_vtypescfg, l_tripfile, self._forcerebuildscenarios)
        self._generateRouteXML(l_netfile, l_tripfile, l_routefile, self._forcerebuildscenarios)

        return {
            "configfile": l_configfile,
            "tripinfofile": l_tripinfofile,
            "fcdfile": l_fcdfile,
            "settingsfile": l_settingsfile
        }

    def _generateNodeXML(self, p_scenarioconfig, p_nodefile, p_forcerebuildscenarios=False):
        if os.path.isfile(p_nodefile) and not p_forcerebuildscenarios:
            return

        # parameters
        l_length = p_scenarioconfig.get("parameters").get("length")
        l_nbswitches = p_scenarioconfig.get("parameters").get("switches")
        l_segmentlength = l_length / ( l_nbswitches + 1 )

        if self._onlyoneotlsegment:
            l_length = 2*l_segmentlength # two times segment length

        l_nodes = etree.Element("nodes")
        etree.SubElement(l_nodes, "node", attrib={"id": "2_1_start", "x": "0", "y": "0"})
        etree.SubElement(l_nodes, "node", attrib={"id": "2_1_end", "x": str(l_length), "y": "0"})
        # dummy node for easier from-to routing

        etree.SubElement(l_nodes, "node", attrib={"id": "ramp_exit", "x": str(l_length+l_segmentlength), "y": "0"})

        with open(p_nodefile, "w") as f_pnodesxml:
            f_pnodesxml.write(etree.tostring(l_nodes, pretty_print=True))

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
        l_edges = etree.Element("edges")
        l_21edge = etree.SubElement(l_edges, "edge", attrib={"id": "2_1_segment",
                                                                   "from" : "2_1_start",
                                                                   "to": "2_1_end",
                                                                   "numLanes": "2",
                                                                   "speed": str(l_maxspeed)})

        # add splits and joins
        l_addotllane = False
        for i_segmentpos in xrange(0,int(l_length),int(l_segmentlength)) \
                if not self._onlyoneotlsegment else xrange(0,int(2*l_segmentlength),int(l_segmentlength)):
            etree.SubElement(l_21edge, "split", attrib={"pos": str(i_segmentpos),
                                                              "lanes": "0 1" if l_addotllane else "0",
                                                              "speed": str(l_maxspeed)})
            l_addotllane ^= True

        # dummy edge
        etree.SubElement(l_edges, "edge", attrib={"id": "2_1_end-ramp_exit",
                                                        "from" : "2_1_end",
                                                        "to": "ramp_exit",
                                                        "numLanes": "1",
                                                        "speed": str(l_maxspeed)})

        with open(p_edgefile, "w") as f_pedgexml:
            f_pedgexml.write(etree.tostring(l_edges, pretty_print=True))

    def _generateAdditionalXML(self, p_scenarioconfig, p_initialsorting, p_run, p_scenarioname, p_additionalfile, p_forcerebuildscenarios):
        if os.path.isfile(p_additionalfile) and not p_forcerebuildscenarios:
            return

        # parameters
        l_length = p_scenarioconfig.get("parameters").get("length")
        l_nbswitches = p_scenarioconfig.get("parameters").get("switches")
        # assume even distributed otl segment lengths
        l_segmentlength = l_length / ( l_nbswitches + 1 )

        l_additional = etree.Element("additional")
        # place induction loop right before the first split (i.e. end of starting edge)
        #     <inductionLoop id="myLoop1" lane="foo_0" pos="42" freq="900" file="out.xml"/>
        etree.SubElement(l_additional, "inductionLoop",
                               attrib={
                                   "id": "pre",
                                   "lane": "2_1_segment_0",
                                   "pos": str(l_segmentlength-5),
                                   "friendlyPos": "true",
                                   "splitByType": "true",
                                   "freq" : "1",
                                   "file": os.path.join(self.getSUMOConfigDir(), p_scenarioname, str(p_initialsorting), str(p_run), "{}.inductionLoop.start.xml".format(p_scenarioname))
                               })

        etree.SubElement(l_additional, "inductionLoop",
                               attrib={
                                   "id": "post",
                                   "lane": "2_1_end-ramp_exit_0",
                                   "pos": str(l_segmentlength-5),
                                   "friendlyPos": "true",
                                   "splitByType": "true",
                                   "freq" : "1",
                                   "file": os.path.join(self.getSUMOConfigDir(), p_scenarioname, str(p_initialsorting), str(p_run), "{}.inductionLoop.exit.xml".format(p_scenarioname))
                               })

        with open(p_additionalfile, "w") as f_paddxml:
            f_paddxml.write(etree.tostring(l_additional, pretty_print=True))

    ## create sumo config
    def _generateConfigXML(self, p_configfile, p_netfile, p_routefile, p_additionalfile, p_settingsfile, p_simtimeinterval, p_forcerebuildscenarios=False):
        if os.path.isfile(p_configfile) and not p_forcerebuildscenarios:
            return
        assert type(p_simtimeinterval) == list and len(p_simtimeinterval) == 2

        l_configuration = etree.Element("configuration")
        l_input = etree.SubElement(l_configuration, "input")
        etree.SubElement(l_input, "net-file", attrib={"value": p_netfile})
        etree.SubElement(l_input, "route-files", attrib={"value": p_routefile})
        etree.SubElement(l_input, "additional-files", attrib={"value": p_additionalfile})
        etree.SubElement(l_input, "gui-settings-file", attrib={"value": p_settingsfile})
        l_time = etree.SubElement(l_configuration, "time")
        etree.SubElement(l_time, "begin", attrib={"value": str(p_simtimeinterval[0])})

        with open(p_configfile, "w") as f_pconfigxml:
            f_pconfigxml.write(etree.tostring(l_configuration, pretty_print=True))

    def _generateSettingsXML(self, p_scenarioconfig, p_runcfg, p_settingsfile, p_forcerebuildscenarios=False):
        if os.path.isfile(p_settingsfile) and not p_forcerebuildscenarios:
            return

        l_viewsettings = etree.Element("viewsettings")
        etree.SubElement(l_viewsettings, "viewport",
                               attrib={"x": str(p_scenarioconfig.get("parameters").get("length") / 2),
                                       "y": "0",
                                       "zoom": "100"})
        etree.SubElement(l_viewsettings, "delay", attrib={"value": str(p_runcfg.get("sumo").get("gui-delay"))})

        with open(p_settingsfile, "w") as f_pconfigxml:
            f_pconfigxml.write(etree.tostring(l_viewsettings, pretty_print=True))

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
            lambda vtype: Vehicle(p_vtypescfg.get(vtype), p_vtypedistribution.get(vtype).get("speedDev")),
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
        assert p_initialsorting in ["best", "random", "worst"]

        if p_initialsorting == "best":
            l_vehicles.sort(key=lambda v: v.getMaxSpeed(), reverse=True)
        elif p_initialsorting == "worst":
            l_vehicles.sort(key=lambda v: v.getMaxSpeed())

        # assign start time and id to each vehicle
        for i,i_vehicle in enumerate(l_vehicles):
            i_vehicle.provision("vehicle{}".format(i),
                                self._nextTime(l_vehps,
                                               l_vehicles[i-1].getStartTime() if i > 0 else 0,
                                               p_runcfg.get("starttimedistribution")))

        return l_vehicles

    def _generateTripXML(self, p_scenarioconfig, p_runcfg, p_initialsorting, p_vtypescfg, p_tripfile, p_forcerebuildscenarios=False):
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
                                                                 p_initialsorting,
                                                                 p_runcfg.get("vtypedistribution")
                                                                 )


        # xml
        l_trips = etree.Element("trips")

        # create a sumo vtype for each vehicle
        for i_vehicle in l_vehicles:

            # filter for relevant attributes
            l_vattr = dict( map( lambda (k, v): (k, str(v)), filter(
                lambda (k, v): k in ["vClass","length","width","height","minGap","accel","decel","speedFactor","speedDev"], i_vehicle.getVType().iteritems()
            )))

            l_vattr["id"] = str(i_vehicle.getID())
            l_vattr["color"] = "{},{},{},{}".format(*i_vehicle.getColor())
            # override parameters speedDev, desiredSpeed, and length if defined in run config
            l_runcfgspeeddev = self.getRunConfig().get("vtypedistribution").get(l_vattr.get("vClass")).get("speedDev")
            if l_runcfgspeeddev != None:
                l_vattr["speedDev"] = str(l_runcfgspeeddev)

            l_runcfgdesiredspeed = self.getRunConfig().get("vtypedistribution").get(l_vattr.get("vClass")).get("desiredSpeed")
            l_vattr["maxSpeed"] = str(l_runcfgdesiredspeed) if l_runcfgdesiredspeed != None else str(i_vehicle.getMaxSpeed())

            l_runcfglength = self.getRunConfig().get("vtypedistribution").get(l_vattr.get("vClass")).get("length")
            if l_runcfglength != None:
                l_vattr["length"] = str(l_runcfglength)

            # fix tractor vClass to trailer
            if l_vattr["vClass"] == "tractor":
                l_vattr["vClass"] = "trailer"
            l_vattr["type"] = l_vattr.get("vClass")

            etree.SubElement(l_trips, "vType", attrib=l_vattr)

        # add trips
        for i_vehicle in l_vehicles:
            etree.SubElement(l_trips, "trip", attrib={
                "id": i_vehicle.getID(),
                "depart": str(i_vehicle.getStartTime()),
                "from": "2_1_segment",
                "to": "2_1_end-ramp_exit",
                "type": i_vehicle.getID(),
                "departSpeed": "max",
            })

        with open(p_tripfile, "w") as f_ptripxml:
            f_ptripxml.write(etree.tostring(l_trips, pretty_print=True))

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

