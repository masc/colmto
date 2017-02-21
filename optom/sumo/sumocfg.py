# -*- coding: utf-8 -*-
# @package optom
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of Overtaking Manoeuvres project.   #
# # Copyright (c) 2017, Malte Aschermann (malte.aschermann@tu-clausthal.de)   #
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
"""This module generates static sumo configuration files for later execution."""
from __future__ import division
from __future__ import print_function

import copy
import itertools
import os
import random
import subprocess
from collections import OrderedDict

import numpy

import optom.common.configuration
import optom.common.io
import optom.common.log
import optom.common.visualisation
import optom.environment.vehicle


class SumoConfig(optom.common.configuration.Configuration):
    """Create SUMO configuration files"""

    def __init__(self, args, netconvertbinary, duarouterbinary):
        """C'tor"""
        super(SumoConfig, self).__init__(args)

        self._log = optom.common.log.logger(__name__, args.loglevel, args.quiet, args.logfile)
        self._writer = optom.common.io.Writer(args)

        self._binaries = {
            "netconvert": netconvertbinary,
            "duarouter": duarouterbinary
        }

        if not os.path.exists(self.sumo_config_dir):
            os.makedirs(self.sumo_config_dir)

        if not os.path.exists(self.runsdir):
            os.makedirs(self.runsdir)

        if not os.path.exists(self.resultsdir):
            os.makedirs(self.resultsdir)

        if self._args.forcerebuildscenarios:
            self._log.debug(
                "--force-rebuild-scenarios set "
                "-> rebuilding/overwriting scenarios if already present"
            )

        # generate color map for vehicle max speeds
        l_global_maxspeed = max(
            [
                i_scenario.get("parameters").get("speedlimit")
                for i_scenario in self.scenario_config.itervalues()
                ]
        )
        self._speed_colormap = optom.common.visualisation.mapped_cmap(
            "plasma",
            l_global_maxspeed
        )

    @property
    def sumo_config_dir(self):
        """
        Returns:
             directory of SUMO config
        """
        return os.path.join(self.output_dir, "SUMO")

    @property
    def runsdir(self):
        """
        Returns:
             directory of runs
        """
        return os.path.join(self.output_dir, "SUMO", self.run_prefix, "runs")

    @property
    def resultsdir(self):
        """
        Returns:
            directory for results
        """
        return os.path.join(self.output_dir, "SUMO", self.run_prefix, "results")

    @property
    def sumo_run_config(self):
        """
        Returns:
             copy of sumo run config
        """
        return copy.copy(
            self.run_config.get("sumo")
        )

    def generate_scenario(self, scenarioname):
        """generate SUMO scenario based on scenario name"""

        self._log.debug("Generating scenario %s", scenarioname)

        l_destinationdir = os.path.join(self.runsdir, scenarioname)
        if not os.path.exists(os.path.join(l_destinationdir)):
            os.mkdir(l_destinationdir)

        l_scenarioconfig = self.scenario_config.get(scenarioname)

        l_scenarioruns = {
            "scenarioname": scenarioname,
            "runs": {}
        }

        l_nodefile = l_scenarioruns["nodefile"] = os.path.join(
            l_destinationdir, "{}.nod.xml".format(scenarioname)
        )
        l_edgefile = l_scenarioruns["edgefile"] = os.path.join(
            l_destinationdir, "{}.edg.xml".format(scenarioname)
        )
        l_netfile = l_scenarioruns["netfile"] = os.path.join(
            l_destinationdir, "{}.net.xml".format(scenarioname)
        )
        l_settingsfile = l_scenarioruns["settingsfile"] = os.path.join(
            l_destinationdir, "{}.settings.xml".format(scenarioname)
        )

        self._generate_node_xml(
            l_scenarioconfig, l_nodefile, self._args.forcerebuildscenarios
        )
        self._generate_edge_xml(
            scenarioname, l_scenarioconfig, l_edgefile, self._args.forcerebuildscenarios
        )
        self._generate_settings_xml(
            l_scenarioconfig, self.run_config, l_settingsfile, self._args.forcerebuildscenarios
        )
        self._generate_net_xml(
            l_nodefile, l_edgefile, l_netfile, self._args.forcerebuildscenarios
        )

        return l_scenarioruns

    def generate_run(self, scenario_run_config, initial_sorting, run_number):
        """generate run configurations

        @param scenario_run_config: run configuration of scenario
        @param initial_sorting: initial sorting of vehicles ("best", "random", "worst")
        @param run_number: number of current run
        @retval
            run configuration dictionary
        """
        self._log.debug("Generating run %s for %s sorting", run_number, initial_sorting)

        l_destinationdir = os.path.join(self.runsdir, scenario_run_config.get("scenarioname"))
        if not os.path.exists(os.path.join(l_destinationdir)):
            os.mkdir(l_destinationdir)

        if not os.path.exists(os.path.join(l_destinationdir, str(initial_sorting))):
            os.mkdir(
                os.path.join(os.path.join(l_destinationdir, str(initial_sorting)))
            )

        if not os.path.exists(
                os.path.join(l_destinationdir, str(initial_sorting), str(run_number))):
            os.mkdir(
                os.path.join(
                    os.path.join(l_destinationdir, str(initial_sorting), str(run_number))
                )
            )

        self._log.debug(
            "Generating SUMO run configuration for scenario %s / sorting %s / run %d",
            scenario_run_config.get("scenarioname"), initial_sorting, run_number
        )

        l_tripfile = os.path.join(
            l_destinationdir, str(initial_sorting), str(run_number),
            "{}.trip.xml".format(scenario_run_config.get("scenarioname"))
        )
        l_routefile = os.path.join(
            l_destinationdir, str(initial_sorting), str(run_number),
            "{}.rou.xml".format(scenario_run_config.get("scenarioname"))
        )
        l_configfile = os.path.join(
            l_destinationdir, str(initial_sorting), str(run_number),
            "{}.sumo.cfg".format(scenario_run_config.get("scenarioname"))
        )
        # l_tripinfofile = os.path.join(l_destinationdir, str(initial_sorting), str(run_number),
        # "{}.tripinfo-output.xml".format(l_scenarioname))

        l_output_measurements_dir = os.path.join(
            self.resultsdir,
            scenario_run_config.get("scenarioname"),
            str(initial_sorting),
            str(run_number)
        )

        if not os.path.exists(l_output_measurements_dir):
            os.makedirs(l_output_measurements_dir)

        l_fcdfile = os.path.join(
            l_output_measurements_dir,
            "{}.fcd-output.xml".format(scenario_run_config.get("scenarioname"))
        )

        l_runcfgfiles = [l_tripfile, l_routefile, l_configfile]

        if len([fname for fname in l_runcfgfiles if not os.path.isfile(fname)]) > 0:
            self._log.debug(
                "Incomplete/non-existing SUMO run configuration for %s, %s, %d -> (re)building",
                scenario_run_config.get("scenarioname"), initial_sorting, run_number
            )
            self._args.forcerebuildscenarios = True

        self._generate_config_xml(
            {
                "configfile": l_configfile,
                "netfile": scenario_run_config.get("netfile"),
                "routefile": l_routefile,
                "settingsfile": scenario_run_config.get("settingsfile")
            },
            self.run_config.get("simtimeinterval"), self._args.forcerebuildscenarios
        )

        l_vehicles = self._generate_trip_xml(
            scenario_run_config, initial_sorting, l_tripfile,
            self._args.forcerebuildscenarios
        )

        self._generate_route_xml(
            scenario_run_config.get("netfile"), l_tripfile, l_routefile,
            self._args.forcerebuildscenarios
        )

        return {
            "scenarioname": scenario_run_config.get("scenarioname"),
            "sumoport": self.run_config.get("sumo").get("port"),
            "runnumber": run_number,
            "vehicles": l_vehicles,
            "settingsfile": scenario_run_config.get("settingsfile"),
            "tripfile": l_tripfile,
            "routefile": l_routefile,
            "configfile": l_configfile,
            "fcdfile": l_fcdfile,
            "scenario_config": self.scenario_config.get(scenario_run_config.get("scenarioname"))
        }

    def _generate_node_xml(self, scenarioconfig, nodefile, forcerebuildscenarios=False):
        """
        Generate SUMO's node configuration file.

        @param scenarioconfig: Scenario configuration
        @param nodefile: Destination to write node file
        @param forcerebuildscenarios: rebuild scenarios,
                                        even if they already exist for current run
        """

        if os.path.isfile(nodefile) and not forcerebuildscenarios:
            return

        self._log.debug("Generating node xml")

        # parameters
        l_length = scenarioconfig.get("parameters").get("length")
        l_nbswitches = scenarioconfig.get("parameters").get("switches")
        l_segmentlength = l_length / (l_nbswitches + 1)

        if self._args.onlyoneotlsegment:
            l_length = 2 * l_segmentlength  # two times segment length

        l_nodes = optom.common.io.etree.Element("nodes")
        optom.common.io.etree.SubElement(
            l_nodes, "node", attrib={"id": "enter", "x": str(-l_segmentlength), "y": "0"}
        )
        optom.common.io.etree.SubElement(
            l_nodes, "node", attrib={"id": "21start", "x": "0", "y": "0"}
        )
        optom.common.io.etree.SubElement(
            l_nodes, "node", attrib={"id": "21end", "x": str(l_length), "y": "0"}
        )

        # dummy node for easier from-to routing
        optom.common.io.etree.SubElement(
            l_nodes,
            "node",
            attrib={
                "id": "exit",
                "x": str(
                    l_length + 0.1
                    if l_nbswitches % 2 == 1 or self._args.onlyoneotlsegment
                    else l_length + l_segmentlength
                ),
                "y": "0"
            }
        )

        with open(nodefile, "w") as f_nodesxml:
            f_nodesxml.write(optom.common.io.etree.tostring(l_nodes, pretty_print=True))

    def _generate_edge_xml(
            self, scenario_name, scenario_config, edgefile, forcerebuildscenarios=False):
        """
        Generate SUMO's edge configuration file.

        @param scenario_name: Name of scenario (required to id detector positions)
        @param scenario_config: Scenario configuration
        @param edgefile: Destination to write edge file
        @param forcerebuildscenarios: Rebuild scenarios,
                                        even if they already exist for current run
        """

        if os.path.isfile(edgefile) and not forcerebuildscenarios:
            return

        self._log.debug("Generating edge xml for %s", scenario_name)

        # parameters
        l_length = scenario_config.get("parameters").get("length")
        l_nbswitches = scenario_config.get("parameters").get("switches")
        l_maxspeed = scenario_config.get("parameters").get("speedlimit")

        # assume even distributed otl segment lengths
        l_segmentlength = l_length / (l_nbswitches + 1)

        # create edges xml
        l_edges = optom.common.io.etree.Element("edges")

        # Entering edge with one lane, leading to 2+1 Roadway
        optom.common.io.etree.SubElement(
            l_edges,
            "edge",
            attrib={
                "id": "enter_21start",
                "from": "enter",
                "to": "21start",
                "numLanes": "1",
                "speed": str(l_maxspeed)
            }
        )

        # 2+1 Roadway
        l_21edge = optom.common.io.etree.SubElement(
            l_edges,
            "edge",
            attrib={
                "id": "21segment",
                "from": "21start",
                "to": "21end",
                "numLanes": "2",
                "spreadType": "center",
                "speed": str(l_maxspeed)
            }
        )

        # deny access to lane 1 (OTL) to vehicle with vClass "custom2"
        # <lane index="1" disallow="custom2"/>
        optom.common.io.etree.SubElement(
            l_21edge,
            "lane",
            attrib={
                "index": "1",
                "disallow": "custom1"
            }
        )

        if self.scenario_config.get(
                scenario_name
        ).get("parameters").get("detectorpositions") is None:
            self.scenario_config.get(
                scenario_name
            ).get("parameters")["detectorpositions"] = [0, l_segmentlength]

        self._generate_switches(l_21edge, scenario_config)

        # Exit lane
        optom.common.io.etree.SubElement(
            l_edges,
            "edge",
            attrib={
                "id": "21end_exit",
                "from": "21end",
                "to": "exit",
                "numLanes": "1",
                "spreadType": "right",
                "speed": str(l_maxspeed)
            }
        )

        with open(edgefile, "w") as f_edgexml:
            f_edgexml.write(optom.common.io.etree.tostring(l_edges, pretty_print=True))

    def _generate_switches(self, edge, scenario_config):
        """
        Generate switches if not pre-defined in scenario config.

        @param edge: edge
        @param scenario_config: scenario config dictionary
        """
        self._log.info("########### generating switches ###########")

        l_length = scenario_config.get("parameters").get("length")
        l_nbswitches = scenario_config.get("parameters").get("switches")
        l_segmentlength = l_length / (l_nbswitches + 1)
        l_parameters = scenario_config.get("parameters")

        if isinstance(l_parameters.get("switchpositions"), (list, tuple)):
            # add splits and joins
            l_add_otl_lane = True
            for i_segmentpos in l_parameters.get("switchpositions"):
                optom.common.io.etree.SubElement(
                    edge,
                    "split",
                    attrib={
                        "pos": str(i_segmentpos),
                        "lanes": "0 1" if l_add_otl_lane else "0",
                        "speed": str(scenario_config.get("parameters").get("speedlimit"))
                    }
                )

                l_add_otl_lane ^= True
        else:
            self._log.info("Rebuilding switches")
            scenario_config.get("parameters")["switchpositions"] = []
            # compute and add splits and joins
            l_add_otl_lane = True
            for i_segmentpos in xrange(0, int(l_length), int(l_segmentlength)) \
                    if not self._args.onlyoneotlsegment \
                    else xrange(0, int(2 * l_segmentlength - 1), int(l_segmentlength)):
                optom.common.io.etree.SubElement(
                    edge,
                    "split",
                    attrib={
                        "pos": str(i_segmentpos),
                        "lanes": "0 1" if l_add_otl_lane else "0",
                        "speed": str(scenario_config.get("parameters").get("speedlimit"))
                    }
                )

                scenario_config.get(
                    "parameters"
                ).get(
                    "switchpositions"
                ).append(i_segmentpos)

                l_add_otl_lane ^= True

    @staticmethod
    def _generate_config_xml(config_files, simtimeinterval, forcerebuildscenarios=False):
        """
        Generate SUMO's main configuration file.

        @param config_files: Dictionary of config file locations,
                             i.e. netfile, routefile, settingsfile
        @param simtimeinterval: Time interval of simulation
        @param forcerebuildscenarios: Rebuild scenarios,
                                        even if they already exist for current run
        """

        if os.path.isfile(config_files.get("configfile")) and not forcerebuildscenarios:
            return
        assert isinstance(simtimeinterval, list) and len(simtimeinterval) == 2

        l_configuration = optom.common.io.etree.Element("configuration")
        l_input = optom.common.io.etree.SubElement(l_configuration, "input")
        optom.common.io.etree.SubElement(
            l_input,
            "net-file",
            attrib={"value": config_files.get("netfile")}
        )
        optom.common.io.etree.SubElement(
            l_input,
            "route-files",
            attrib={"value": config_files.get("routefile")}
        )
        optom.common.io.etree.SubElement(
            l_input,
            "gui-settings-file",
            attrib={"value": config_files.get("settingsfile")}
        )
        l_time = optom.common.io.etree.SubElement(l_configuration, "time")
        optom.common.io.etree.SubElement(
            l_time,
            "begin",
            attrib={"value": str(simtimeinterval[0])}
        )

        with open(config_files.get("configfile"), "w") as f_configxml:
            f_configxml.write(optom.common.io.etree.tostring(l_configuration, pretty_print=True))

    @staticmethod
    def _generate_settings_xml(
            scenarioconfig, runcfg, settingsfile, forcerebuildscenarios=False):
        """
        Generate SUMO's settings configuration file.

        @param scenarioconfig: Scenario configuration
        @param runcfg: Run configuration
        @param settingsfile: Destination to write settings file
        @param forcerebuildscenarios: Rebuild scenarios,
                                        even if they already exist for current run
        """
        if os.path.isfile(settingsfile) and not forcerebuildscenarios:
            return

        l_viewsettings = optom.common.io.etree.Element("viewsettings")
        optom.common.io.etree.SubElement(
            l_viewsettings, "viewport",
            attrib={"x": str(scenarioconfig.get("parameters").get("length") / 2),
                    "y": "0",
                    "zoom": "100"}
        )
        optom.common.io.etree.SubElement(
            l_viewsettings, "delay", attrib={"value": str(runcfg.get("sumo").get("gui-delay"))}
        )

        with open(settingsfile, "w") as f_configxml:
            f_configxml.write(optom.common.io.etree.tostring(l_viewsettings, pretty_print=True))

    @staticmethod
    def _next_timestep(lamb, prev_start_time, distribution="poisson"):
        r"""
        Calculate next time step in Poisson or linear distribution.

        Poisson (exponential) distribution with
        \f$F(x) := 1 - e^{-\lambda x}\f$
        by using random.expovariate(lamb).

        Linear distribution just adds 1/lamb to the previous start time.

        For every other value of distribution this function just returns the input value of
        prev_start_time.

        @param lamb: lambda
        @param prev_start_time: start time
        @param distribution: distribution, i.e. "poisson" or "linear"
        @retval next start time
        """

        if distribution == "poisson":
            return prev_start_time + random.expovariate(lamb)
        elif distribution == "linear":
            return prev_start_time + 1 / lamb
        else:
            return prev_start_time

    def _create_vehicle_distribution(self, nbvehicles, aadt, initialsorting, scenario_name):
        """
        Create a distribution of vehicles based on

        @param nbvehicles: number of vehicles
        @param aadt: anual average daily traffic (vehicles/day/lane)
        @param initialsorting: initial sorting of vehicles (by max speed)
                                ["best", "random", "worst"]
        @param scenario_name: name of scenario
        @retval OrderedDict of ID -> optom.environment.vehicle.Vehicle
        """

        assert initialsorting in ["best", "random", "worst"]

        self._log.debug(
            "Create vehicle distribution with %s", self._run_config.get("vtypedistribution")
        )

        l_vtypedistribution = list(
            itertools.chain.from_iterable(
                [
                    [k] * int(round(100 * v.get("fraction")))
                    for (k, v) in self._run_config.get("vtypedistribution").iteritems()
                ]
            )
        )

        l_vehps = aadt / (24 * 60 * 60) if not self._run_config.get(
            "vehiclespersecond"
        ).get(
            "enabled"
        ) else self._run_config.get("vehiclespersecond").get("value")

        l_vehicle_list = [
            optom.environment.vehicle.SUMOVehicle(
                vehicle_type=vtype,
                vtype_sumo_cfg=self.vtypes_config.get(vtype),
                speed_deviation=self._run_config.get(
                    "vtypedistribution"
                ).get(vtype).get("speedDev"),
                speed_max=min(
                    random.choice(
                        self._run_config.get("vtypedistribution").get(vtype).get("desiredSpeeds")
                    ),
                    self.scenario_config.get(scenario_name).get("parameters").get("speedlimit")
                )
            ) for vtype in [random.choice(l_vtypedistribution) for _ in xrange(nbvehicles)]
        ]

        # sort speeds according to initial sorting flag
        if initialsorting == "best":
            l_vehicle_list.sort(key=lambda i_v: i_v.speed_max, reverse=True)
        elif initialsorting == "worst":
            l_vehicle_list.sort(key=lambda i_v: i_v.speed_max)
        elif initialsorting == "random":
            random.shuffle(l_vehicle_list)

        # assign a new id according to sort order and starting time to each vehicle
        l_vehicles = OrderedDict()
        for i, i_vehicle in enumerate(l_vehicle_list):
            # update colors
            i_vehicle.color = numpy.array(self._speed_colormap(i_vehicle.speed_max))*255
            # update start time
            i_vehicle.start_time = self._next_timestep(
                l_vehps,
                l_vehicle_list[i - 1].start_time if i > 0 else 0,
                self.run_config.get("starttimedistribution")
            )
            l_vehicles["vehicle{}".format(i)] = i_vehicle

        return l_vehicles

    def _generate_trip_xml(self, scenario_runs, initialsorting, tripfile,
                           forcerebuildscenarios=False):
        """
        Generate SUMO's trip file.

        @param scenario_runs:
        @param initialsorting:
        @param tripfile:
        @param forcerebuildscenarios:
        @retval vehicles
        """

        if os.path.isfile(tripfile) and not forcerebuildscenarios:
            return
        self._log.debug("Generating trip xml for %s", scenario_runs.get("scenarioname"))
        # generate simple traffic demand by considering AADT, Vmax, roadtype etc
        l_aadt = self.scenario_config.get(
            scenario_runs.get("scenarioname")
        ).get(
            "parameters"
        ).get(
            "aadt"
        ) if not self.run_config.get("aadt").get("enabled") \
            else self.run_config.get("aadt").get("value")

        l_timebegin, l_timeend = self.run_config.get("simtimeinterval")

        # number of vehicles = AADT / [seconds of day] * [scenario time in seconds]

        l_numberofvehicles = int(round(l_aadt / (24 * 60 * 60) * (l_timeend - l_timebegin))) \
            if not self.run_config.get("nbvehicles").get("enabled") \
            else self.run_config.get("nbvehicles").get("value")

        self._log.debug(
            "Scenario's AADT of %d vehicles/average annual day"
            "=> %d vehicles for %d simulation seconds",
            l_aadt, l_numberofvehicles, (l_timeend - l_timebegin)
        )

        l_vehicles = self._create_vehicle_distribution(
            l_numberofvehicles,
            l_aadt,
            initialsorting,
            scenario_runs.get("scenarioname")
        )

        # xml
        l_trips = optom.common.io.etree.Element("trips")

        # create a sumo vehicle_type for each vehicle
        for i_vid, i_vehicle in l_vehicles.iteritems():

            # filter for relevant attributes and transform to string
            l_vattr = {k: str(v) for k, v in i_vehicle.properties.iteritems()}
            l_vattr.update({
                "id": str(i_vid),
                "color": "{},{},{},{}".format(*i_vehicle.color/255.)
            })

            # override parameters speedDev, desiredSpeed, and length if defined in run config
            l_runcfgspeeddev = self.run_config \
                .get("vtypedistribution") \
                .get(l_vattr.get("vType")) \
                .get("speedDev")
            if l_runcfgspeeddev is not None:
                l_vattr["speedDev"] = str(l_runcfgspeeddev)

            l_vattr["speedlimit"] = str(i_vehicle.speed_max)
            l_vattr["maxSpeed"] = str(i_vehicle.speed_max)

            l_runcfglength = self.run_config \
                .get("vtypedistribution") \
                .get(l_vattr.get("vType")) \
                .get("length")

            if l_runcfglength is not None:
                l_vattr["length"] = str(l_runcfglength)

            # fix tractor vType to trailer
            if l_vattr["vType"] == "tractor":
                l_vattr["vType"] = "trailer"

            l_vattr["type"] = l_vattr.get("vType")

            optom.common.io.etree.SubElement(l_trips, "vType", attrib=l_vattr)

        # add trip for each vehicle
        for i_vid, i_vehicle in l_vehicles.iteritems():
            optom.common.io.etree.SubElement(l_trips, "trip", attrib={
                "id": i_vid,
                "depart": str(i_vehicle.start_time),
                "from": "enter_21start",
                "to": "21end_exit",
                "type": i_vid,
                "departSpeed": "max",
            })

        with open(tripfile, "w") as f_tripxml:
            f_tripxml.write(optom.common.io.etree.tostring(l_trips, pretty_print=True))

        return l_vehicles

    # create net xml using netconvert
    def _generate_net_xml(
            self, nodefile, edgefile, netfile, forcerebuildscenarios=False):
        """
        Generate SUMO's net xml.

        @param nodefile:
        @param edgefile:
        @param netfile:
        @param forcerebuildscenarios:
        """

        if os.path.isfile(netfile) and not forcerebuildscenarios:
            return

        l_netconvertprocess = subprocess.check_output(
            [
                self._binaries.get("netconvert"),
                "--node-files={}".format(nodefile),
                "--edge-files={}".format(edgefile),
                "--output-file={}".format(netfile)
            ],
            stderr=subprocess.STDOUT
        )
        self._log.debug(
            "%s: %s", self._binaries.get("netconvert"), l_netconvertprocess.replace("\n", "")
        )

    def _generate_route_xml(
            self, netfile, tripfile, routefile, forcerebuildscenarios=False):
        """
        Generate SUMO's route xml.

        @param netfile:
        @param tripfile:
        @param routefile:
        @param forcerebuildscenarios:
        """

        if os.path.isfile(routefile) and not forcerebuildscenarios:
            return

        l_duarouterprocess = subprocess.check_output(
            [
                self._binaries.get("duarouter"),
                "-n", netfile,
                "-t", tripfile,
                "-o", routefile
            ],
            stderr=subprocess.STDOUT
        )
        self._log.debug(
            "%s: %s", self._binaries.get("duarouter"), l_duarouterprocess.replace("\n", "")
        )
