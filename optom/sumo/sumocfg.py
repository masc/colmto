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

    def __init__(self, p_args, p_netconvertbinary, p_duarouterbinary):
        """C'tor"""
        super(SumoConfig, self).__init__(p_args)

        self._log = optom.common.log.logger(__name__, p_args.loglevel, p_args.quiet, p_args.logfile)
        self._writer = optom.common.io.Writer(p_args)

        self._binaries = {
            "netconvert": p_netconvertbinary,
            "duarouter": p_duarouterbinary
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

    def generate_scenario(self, p_scenarioname):
        """generate SUMO scenario based on scenario name"""

        self._log.debug("Generating scenario %s", p_scenarioname)

        l_destinationdir = os.path.join(self.runsdir, p_scenarioname)
        if not os.path.exists(os.path.join(l_destinationdir)):
            os.mkdir(l_destinationdir)

        l_scenarioconfig = self.scenario_config.get(p_scenarioname)

        l_scenarioruns = {
            "scenarioname": p_scenarioname,
            "runs": {}
        }

        l_nodefile = l_scenarioruns["nodefile"] = os.path.join(
            l_destinationdir, "{}.nod.xml".format(p_scenarioname)
        )
        l_edgefile = l_scenarioruns["edgefile"] = os.path.join(
            l_destinationdir, "{}.edg.xml".format(p_scenarioname)
        )
        l_netfile = l_scenarioruns["netfile"] = os.path.join(
            l_destinationdir, "{}.net.xml".format(p_scenarioname)
        )
        l_settingsfile = l_scenarioruns["settingsfile"] = os.path.join(
            l_destinationdir, "{}.settings.xml".format(p_scenarioname)
        )

        self._generate_node_xml(
            l_scenarioconfig, l_nodefile, self._args.forcerebuildscenarios
        )
        self._generate_edge_xml(
            p_scenarioname, l_scenarioconfig, l_edgefile, self._args.forcerebuildscenarios
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

        Args:
            scenario_run_config: run configuration of scenario
            initial_sorting: initial sorting of vehicles ("best", "random", "worst")
            run_number: number of current run
        Returns:
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
            "fcdfile": l_fcdfile
        }

    def _generate_node_xml(self, p_scenarioconfig, p_nodefile, p_forcerebuildscenarios=False):
        """
        Generate SUMO's node configuration file.

        Args:
            p_scenarioconfig: Scenario configuration
            p_nodefile: Destination to write node file
            p_forcerebuildscenarios: rebuild scenarios,
                                        even if they already exist for current run
        """

        if os.path.isfile(p_nodefile) and not p_forcerebuildscenarios:
            return

        self._log.debug("Generating node xml")

        # parameters
        l_length = p_scenarioconfig.get("parameters").get("length")
        l_nbswitches = p_scenarioconfig.get("parameters").get("switches")
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

        with open(p_nodefile, "w") as f_pnodesxml:
            f_pnodesxml.write(optom.common.io.etree.tostring(l_nodes, pretty_print=True))

    def _generate_edge_xml(
            self, p_scenario_name, p_scenario_config, p_edgefile, p_forcerebuildscenarios=False):
        """
        Generate SUMO's edge configuration file.

        Args:
            p_scenario_name: Name of scenario (required to id detector positions)
            p_scenario_config: Scenario configuration
            p_edgefile: Destination to write edge file
            p_forcerebuildscenarios: Rebuild scenarios,
                                        even if they already exist for current run
        """

        if os.path.isfile(p_edgefile) and not p_forcerebuildscenarios:
            return

        self._log.debug("Generating edge xml for %s", p_scenario_name)

        # parameters
        l_length = p_scenario_config.get("parameters").get("length")
        l_nbswitches = p_scenario_config.get("parameters").get("switches")
        l_maxspeed = p_scenario_config.get("parameters").get("speedlimit")

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
                p_scenario_name
        ).get("parameters").get("detectorpositions") is None:
            self.scenario_config.get(
                p_scenario_name
            ).get("parameters")["detectorpositions"] = [0, l_segmentlength]

        self._generate_switches(l_21edge, p_scenario_config)

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

        with open(p_edgefile, "w") as f_pedgexml:
            f_pedgexml.write(optom.common.io.etree.tostring(l_edges, pretty_print=True))

    def _generate_switches(self, p_21edge, p_scenario_config):
        """
        Generate switches if not pre-defined in scenario config.

        Args:
            p_21edge: edge
            p_scenario_config: scenario config dictionary
        """
        self._log.info("########### generating switches ###########")

        l_length = p_scenario_config.get("parameters").get("length")
        l_nbswitches = p_scenario_config.get("parameters").get("switches")
        l_segmentlength = l_length / (l_nbswitches + 1)
        l_parameters = p_scenario_config.get("parameters")

        if isinstance(l_parameters.get("switchpositions"), (list, tuple)):
            # add splits and joins
            for i_segmentpos in l_parameters.get("switchpositions"):

                l_add_otl_lane = True
                optom.common.io.etree.SubElement(
                    p_21edge,
                    "split",
                    attrib={
                        "pos": str(i_segmentpos),
                        "lanes": "0 1" if l_add_otl_lane else "0",
                        "speed": str(p_scenario_config.get("parameters").get("speedlimit"))
                    }
                )
        else:
            self._log.info("Rebuilding switches")
            p_scenario_config.get("parameters")["switchpositions"] = []
            # compute and add splits and joins
            l_add_otl_lane = True
            for i_segmentpos in xrange(0, int(l_length), int(l_segmentlength)) \
                    if not self._args.onlyoneotlsegment \
                    else xrange(0, int(2 * l_segmentlength - 1), int(l_segmentlength)):
                optom.common.io.etree.SubElement(
                    p_21edge,
                    "split",
                    attrib={
                        "pos": str(i_segmentpos),
                        "lanes": "0 1" if l_add_otl_lane else "0",
                        "speed": str(p_scenario_config.get("parameters").get("speedlimit"))
                    }
                )

                p_scenario_config.get(
                    "parameters"
                ).get(
                    "switchpositions"
                ).append(i_segmentpos)

                l_add_otl_lane ^= True

    @staticmethod
    def _generate_config_xml(p_config_files, p_simtimeinterval, p_forcerebuildscenarios=False):
        """
        Generate SUMO's main configuration file.

        Args:
            p_config_files: Dictionary of config file locations,
                             i.e. netfile, routefile, settingsfile
            p_simtimeinterval: Time interval of simulation
            p_forcerebuildscenarios: Rebuild scenarios,
                                        even if they already exist for current run
        """

        if os.path.isfile(p_config_files.get("configfile")) and not p_forcerebuildscenarios:
            return
        assert isinstance(p_simtimeinterval, list) and len(p_simtimeinterval) == 2

        l_configuration = optom.common.io.etree.Element("configuration")
        l_input = optom.common.io.etree.SubElement(l_configuration, "input")
        optom.common.io.etree.SubElement(
            l_input,
            "net-file",
            attrib={"value": p_config_files.get("netfile")}
        )
        optom.common.io.etree.SubElement(
            l_input,
            "route-files",
            attrib={"value": p_config_files.get("routefile")}
        )
        optom.common.io.etree.SubElement(
            l_input,
            "gui-settings-file",
            attrib={"value": p_config_files.get("settingsfile")}
        )
        l_time = optom.common.io.etree.SubElement(l_configuration, "time")
        optom.common.io.etree.SubElement(
            l_time,
            "begin",
            attrib={"value": str(p_simtimeinterval[0])}
        )

        with open(p_config_files.get("configfile"), "w") as f_pconfigxml:
            f_pconfigxml.write(optom.common.io.etree.tostring(l_configuration, pretty_print=True))

    @staticmethod
    def _generate_settings_xml(
            p_scenarioconfig, p_runcfg, p_settingsfile, p_forcerebuildscenarios=False):
        """
        Generate SUMO's settings configuration file.

        Args:
            p_scenarioconfig: Scenario configuration
            p_runcfg: Run configuration
            p_settingsfile: Destination to write settings file
            p_forcerebuildscenarios: Rebuild scenarios,
                                        even if they already exist for current run
        """
        if os.path.isfile(p_settingsfile) and not p_forcerebuildscenarios:
            return

        l_viewsettings = optom.common.io.etree.Element("viewsettings")
        optom.common.io.etree.SubElement(
            l_viewsettings, "viewport",
            attrib={"x": str(p_scenarioconfig.get("parameters").get("length") / 2),
                    "y": "0",
                    "zoom": "100"}
        )
        optom.common.io.etree.SubElement(
            l_viewsettings, "delay", attrib={"value": str(p_runcfg.get("sumo").get("gui-delay"))}
        )

        with open(p_settingsfile, "w") as f_pconfigxml:
            f_pconfigxml.write(optom.common.io.etree.tostring(l_viewsettings, pretty_print=True))

    @staticmethod
    def _next_timestep(p_lambda, p_prev_start_time, p_distribution="poisson"):
        """
        Calculate next time step in Poisson or linear distribution.

        Poisson (exponential) distribution with
        $$F(x) := 1 - e^{-lambda x}$$
        by using random.expovariate(p_lambda).

        Linear distribution just adds 1/p_lambda to the previous start time.

        For every other value of p_distribution this function just returns the input value of p_prev_start_time.

        Args:
            p_lambda: lambda
            p_prev_start_time: start time
            p_distribution: distribution, i.e. "poisson" or "linear"
        Returns:
            next start time
        """

        if p_distribution == "poisson":
            return p_prev_start_time + random.expovariate(p_lambda)
        elif p_distribution == "linear":
            return p_prev_start_time + 1 / p_lambda
        else:
            return p_prev_start_time

    def _create_vehicle_distribution(self, p_nbvehicles, p_aadt, p_initialsorting, p_scenario_name):
        """
        Create a distribution of vehicles based on

        Args:
            p_nbvehicles: number of vehicles
            p_aadt: anual average daily traffic (vehicles/day/lane)
            p_initialsorting: initial sorting of vehicles (by max speed)
                                ["best", "random", "worst"]
            p_scenario_name: name of scenario
        Returns:
            OrderedDict of ID -> optom.environment.vehicle.Vehicle
        """

        assert p_initialsorting in ["best", "random", "worst"]

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

        l_vehps = p_aadt / (24 * 60 * 60) if not self._run_config.get(
            "vehiclespersecond"
        ).get(
            "enabled"
        ) else self._run_config.get("vehiclespersecond").get("value")

        l_vehicle_list = [
            optom.environment.vehicle.SUMOVehicle(
                vtype=vtype,
                vtype_sumo_cfg=self.vtypes_config.get(vtype),
                speed_deviation=self._run_config.get(
                    "vtypedistribution"
                ).get(vtype).get("speedDev"),
                speed_max=min(
                    random.choice(
                        self._run_config.get("vtypedistribution").get(vtype).get("desiredSpeeds")
                    ),
                    self.scenario_config.get(p_scenario_name).get("parameters").get("speedlimit")
                )
            ) for vtype in [random.choice(l_vtypedistribution) for _ in xrange(p_nbvehicles)]
            ]

        # sort speeds according to initial sorting flag
        if p_initialsorting == "best":
            l_vehicle_list.sort(key=lambda i_v: i_v.speed_max, reverse=True)
        elif p_initialsorting == "worst":
            l_vehicle_list.sort(key=lambda i_v: i_v.speed_max)
        elif p_initialsorting == "random":
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

    def _generate_trip_xml(self, p_scenario_runs, p_initialsorting, p_tripfile,
                           p_forcerebuildscenarios=False):
        """
        Generate SUMO's trip file.

        Args:
            p_scenario_runs:
            p_initialsorting:
            p_tripfile:
            p_forcerebuildscenarios:
        Returns:
            vehicles
        """

        if os.path.isfile(p_tripfile) and not p_forcerebuildscenarios:
            return
        self._log.debug("Generating trip xml for %s", p_scenario_runs.get("scenarioname"))
        # generate simple traffic demand by considering AADT, Vmax, roadtype etc
        l_aadt = self.scenario_config.get(
            p_scenario_runs.get("scenarioname")
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
            p_initialsorting,
            p_scenario_runs.get("scenarioname")
        )

        # xml
        l_trips = optom.common.io.etree.Element("trips")

        # create a sumo vtype for each vehicle
        for i_vid, i_vehicle in l_vehicles.iteritems():

            # filter for relevant attributes and transform to string
            l_vattr = i_vehicle.vtype_sumo_cfg
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

            l_runcfgdesiredspeed = self.run_config \
                .get("vtypedistribution"). \
                get(l_vattr.get("vType")). \
                get("desiredSpeed")

            l_vattr["speedlimit"] = str(l_runcfgdesiredspeed) \
                if l_runcfgdesiredspeed is not None else str(i_vehicle.speed_max)

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

        with open(p_tripfile, "w") as f_ptripxml:
            f_ptripxml.write(optom.common.io.etree.tostring(l_trips, pretty_print=True))

        return l_vehicles

    # create net xml using netconvert
    def _generate_net_xml(
            self, p_nodefile, p_edgefile, p_netfile, p_forcerebuildscenarios=False):
        """
        Generate SUMO's net xml.

        Args:
            p_nodefile:
            p_edgefile:
            p_netfile:
            p_forcerebuildscenarios:
        """

        if os.path.isfile(p_netfile) and not p_forcerebuildscenarios:
            return

        l_netconvertprocess = subprocess.check_output(
            [
                self._binaries.get("netconvert"),
                "--node-files={}".format(p_nodefile),
                "--edge-files={}".format(p_edgefile),
                "--output-file={}".format(p_netfile)
            ],
            stderr=subprocess.STDOUT
        )
        self._log.debug(
            "%s: %s", self._binaries.get("netconvert"), l_netconvertprocess.replace("\n", "")
        )

    def _generate_route_xml(
            self, p_netfile, p_tripfile, p_routefile, p_forcerebuildscenarios=False):
        """
        Generate SUMO's route xml.

        Args:
            p_netfile:
            p_tripfile:
            p_routefile:
            p_forcerebuildscenarios:
        """

        if os.path.isfile(p_routefile) and not p_forcerebuildscenarios:
            return

        l_duarouterprocess = subprocess.check_output(
            [
                self._binaries.get("duarouter"),
                "-n", p_netfile,
                "-t", p_tripfile,
                "-o", p_routefile
            ],
            stderr=subprocess.STDOUT
        )
        self._log.debug(
            "%s: %s", self._binaries.get("duarouter"), l_duarouterprocess.replace("\n", "")
        )
