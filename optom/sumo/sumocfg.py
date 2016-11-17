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

import optom.common.colormaps
import optom.common.configuration
import optom.common.io
import optom.common.log
import optom.environment.vehicle


class SumoConfig(optom.common.configuration.Configuration):
    """Create SUMO configuration files"""

    def __init__(self, p_args, p_netconvertbinary, p_duarouterbinary):
        """C'tor"""
        super(SumoConfig, self).__init__(p_args)

        self._log = optom.common.log.logger(__name__, p_args.loglevel, p_args.quiet, p_args.logfile)
        self._writer = optom.common.io.Writer(p_args)
        self._args = copy.copy(p_args)
        self._dirs = {
            "sumoconfig": os.path.join(self.outputdir, "SUMO"),
            "runs": os.path.join(self.outputdir, "SUMO", self._runprefix, "runs"),
            "results": os.path.join(self.outputdir, "SUMO", self._runprefix, "results")
        }
        self._binaries = {
            "netconvert": p_netconvertbinary,
            "duarouter": p_duarouterbinary
        }

        if not os.path.exists(self._dirs.get("sumoconfig")):
            os.makedirs(self._dirs.get("sumoconfig"))

        if not os.path.exists(self._dirs.get("runs")):
            os.makedirs(self._dirs.get("runs"))

        if not os.path.exists(self._dirs.get("results")):
            os.makedirs(self._dirs.get("results"))

        if self._args.forcerebuildscenarios:
            self._log.debug(
                "--force-rebuild-scenarios set "
                "-> rebuilding/overwriting scenarios if already present"
            )
        self._onlyoneotlsegment = p_args.onlyoneotlsegment

        # generate color map for vehicle max speeds
        l_global_maxspeed = max(
            [
                i_scenario.get("parameters").get("speedlimit")
                for i_scenario in self.scenarioconfig.itervalues()
                ]
        )
        self._speed_colormap = optom.common.colormaps.get_mapped_cmap(
            "plasma",
            l_global_maxspeed
        )

    @property
    def sumoconfigdir(self):
        """return directory of SUMO config"""
        return self._dirs.get("sumoconfig")

    @property
    def runsdir(self):
        """return directory of runs"""
        return self._dirs.get("runs")

    @property
    def resultsdir(self):
        """return directory of results"""
        return self._dirs.get("results")

    def get(self, p_key):
        """return element of sumo config"""
        return self.runconfig.get("sumo").get(p_key)

    def generate_scenario(self, p_scenarioname):
        """generate SUMO scenario based on scenario name"""

        self._log.debug("Generating scenario %s", p_scenarioname)

        l_destinationdir = os.path.join(self._dirs.get("runs"), p_scenarioname)
        if not os.path.exists(os.path.join(l_destinationdir)):
            os.mkdir(l_destinationdir)

        l_scenarioconfig = self.scenarioconfig.get(p_scenarioname)

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

        self._generate_node_xml(l_scenarioconfig, l_nodefile, self._args.forcerebuildscenarios)
        self._generate_edge_xml(
            p_scenarioname, l_scenarioconfig, l_edgefile, self._args.forcerebuildscenarios
        )
        self._generate_settings_xml(
            l_scenarioconfig, self.runconfig, l_settingsfile, self._args.forcerebuildscenarios
        )
        self._generate_net_xml(l_nodefile, l_edgefile, l_netfile, self._args.forcerebuildscenarios)

        return l_scenarioruns

    def generate_run(self, p_scenarioruns, p_initialsorting, p_run_number):
        """generate run configurations

        :param p_scenarioruns: run configuration of scenario
        :param p_initialsorting: initial sorting of vehicles ("best", "random", "worst")
        :param p_run_number: number of current run
        """
        self._log.debug("Generating run %s for %s sorting", p_run_number, p_initialsorting)

        l_scenario = {
            "name": p_scenarioruns.get("scenarioname"),
            "config": self.scenarioconfig.get(p_scenarioruns.get("scenarioname"))
        }
        l_destinationdir = os.path.join(self._dirs.get("runs"), l_scenario.get("name"))
        if not os.path.exists(os.path.join(l_destinationdir)):
            os.mkdir(l_destinationdir)

        if not os.path.exists(os.path.join(l_destinationdir, str(p_initialsorting))):
            os.mkdir(
                os.path.join(os.path.join(l_destinationdir, str(p_initialsorting)))
            )

        if not os.path.exists(
                os.path.join(l_destinationdir, str(p_initialsorting), str(p_run_number))):
            os.mkdir(
                os.path.join(
                    os.path.join(l_destinationdir, str(p_initialsorting), str(p_run_number))
                )
            )

        self._log.debug(
            "Generating SUMO run configuration for scenario %s / sorting %s / run %d",
            l_scenario.get("name"), p_initialsorting, p_run_number
        )

        l_netfile = p_scenarioruns.get("netfile")
        l_settingsfile = p_scenarioruns.get("settingsfile")

        l_additionalfile = os.path.join(
            l_destinationdir, str(p_initialsorting), str(p_run_number),
            "{}.add.xml".format(l_scenario.get("name"))
        )
        l_tripfile = os.path.join(
            l_destinationdir, str(p_initialsorting), str(p_run_number),
            "{}.trip.xml".format(l_scenario.get("name"))
        )
        l_routefile = os.path.join(
            l_destinationdir, str(p_initialsorting), str(p_run_number),
            "{}.rou.xml".format(l_scenario.get("name"))
        )
        l_configfile = os.path.join(
            l_destinationdir, str(p_initialsorting), str(p_run_number),
            "{}.sumo.cfg".format(l_scenario.get("name"))
        )
        # l_tripinfofile = os.path.join(l_destinationdir, str(p_initialsorting), str(p_run_number),
        # "{}.tripinfo-output.xml".format(l_scenarioname))

        l_iloopdir = os.path.join(
            self._dirs.get("results"),
            l_scenario.get("name"),
            str(p_initialsorting),
            str(p_run_number)
        )

        if not os.path.exists(l_iloopdir):
            os.makedirs(l_iloopdir)

        l_iloopfile = os.path.join(
            l_iloopdir, "{}.inductionLoops.xml".format(l_scenario.get("name"))
        )

        # l_fcdfile = os.path.join(l_destinationdir, str(p_initialsorting),
        #                          str(p_run_number),
        #                          "{}.fcd-output.xml".format(l_scenario.get("name"))
        #                         )

        l_runcfgfiles = [l_tripfile, l_additionalfile, l_routefile, l_configfile]

        if len([fname for fname in l_runcfgfiles if not os.path.isfile(fname)]) > 0:
            self._log.debug(
                "Incomplete/non-existing SUMO run configuration for %s, %s, %d -> (re)building",
                l_scenario.get("name"), p_initialsorting, p_run_number
            )
            self._args.forcerebuildscenarios = True

        self._generate_additional_xml(
            l_scenario.get("name"), l_scenario.get("config"), l_iloopfile, l_additionalfile,
            self._args.forcerebuildscenarios
        )
        self._generate_config_xml(
            l_configfile, l_netfile, l_routefile, l_additionalfile, l_settingsfile,
            self.runconfig.get("simtimeinterval"), self._args.forcerebuildscenarios
        )
        l_vehicles = self._generate_trip_xml(
            l_scenario.get("config"), self.runconfig, p_initialsorting, l_tripfile,
            l_scenario.get("name"), self._args.forcerebuildscenarios
        )
        self._generate_route_xml(
            l_netfile, l_tripfile, l_routefile,
            self._args.forcerebuildscenarios
        )

        return {
            "vehicles": l_vehicles,
            "settingsfile": l_settingsfile,
            "additionalfile": l_additionalfile,
            "tripfile": l_tripfile,
            "routefile": l_routefile,
            "configfile": l_configfile,
            "iloopfile": l_iloopfile
        }

    def _generate_node_xml(self, p_scenarioconfig, p_nodefile, p_forcerebuildscenarios=False):
        """
        Generate SUMO's node configuration file.

        :param p_scenarioconfig: Scenario configuration
        :param p_nodefile: Destination to write node file
        :param p_forcerebuildscenarios: rebuild scenarios,
                                        even if they already exist for current run
        """

        if os.path.isfile(p_nodefile) and not p_forcerebuildscenarios:
            return

        self._log.debug("Generating node xml")

        # parameters
        l_length = p_scenarioconfig.get("parameters").get("length")
        l_nbswitches = p_scenarioconfig.get("parameters").get("switches")
        l_segmentlength = l_length / (l_nbswitches + 1)

        if self._onlyoneotlsegment:
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
                    if l_nbswitches % 2 == 1 or self._onlyoneotlsegment
                    else l_length + l_segmentlength
                ),
                "y": "0"
            }
        )

        with open(p_nodefile, "w") as f_pnodesxml:
            f_pnodesxml.write(optom.common.io.etree.tostring(l_nodes, pretty_print=True))

    def _generate_edge_xml(
            self, p_scenario_name, p_scenarioconfig, p_edgefile, p_forcerebuildscenarios=False):
        """
        Generate SUMO's edge configuration file.

        :param p_scenario_name: Name of scenario (required to id detector positions)
        :param p_scenarioconfig: Scenario configuration
        :param p_edgefile: Destination to write edge file
        :param p_forcerebuildscenarios: Rebuild scenarios,
                                        even if they already exist for current run
        """

        if os.path.isfile(p_edgefile) and not p_forcerebuildscenarios:
            return

        self._log.debug("Generating edge xml for %s", p_scenario_name)

        # parameters
        l_length = p_scenarioconfig.get("parameters").get("length")
        l_nbswitches = p_scenarioconfig.get("parameters").get("switches")
        l_maxspeed = p_scenarioconfig.get("parameters").get("speedlimit")

        # assume even distributed otl segment lengths
        l_segmentlength = l_length / (l_nbswitches + 1)

        # create edges xml
        l_edges = optom.common.io.etree.Element("edges")

        # # find slowest vehicle speed to be used as parameter for entering lane
        # l_lowestspeed = min(
        #     map(lambda vtype: min(vtype.get("desiredSpeeds")),
        #         self.runconfig.get("vtypedistribution").itervalues())
        # )

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

        self.scenarioconfig.get(p_scenario_name)["detectorpositions"] = OrderedDict(
            {
                "1_enter": 5,
                "2_21segment.0_begin": l_segmentlength - 5
            })
        self.scenarioconfig.get(p_scenario_name)["switchpositions"] = []

        # add splits and joins
        l_addotllane = True
        for i_segmentpos in xrange(0, int(l_length), int(l_segmentlength)) \
                if not self._onlyoneotlsegment \
                else xrange(0, int(2 * l_segmentlength - 1), int(l_segmentlength)):
            optom.common.io.etree.SubElement(
                l_21edge,
                "split",
                attrib={
                    "pos": str(i_segmentpos),
                    "lanes": "0 1" if l_addotllane else "0",
                    "speed": str(l_maxspeed)
                }
            )

            self.scenarioconfig.get(p_scenario_name).get("switchpositions").append(i_segmentpos)
            l_addotllane ^= True

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

    def _generate_additional_xml(self, p_scenario_name, p_scenarioconfig, p_iloopfile,
                                 p_additionalfile, p_forcerebuildscenarios):
        """
        Generate SUMO's additional configuration file.

        :param p_scenario_name: Name of scenario (required to id detector positions)
        :param p_scenarioconfig: Scenario configuration
        :param p_iloopfile: File to write induction loop detector 'measurements'
        :param p_additionalfile: Destination to write additional cfg file
        :param p_forcerebuildscenarios: Rebuild scenarios,
                                        even if they already exist for current run
        """

        if os.path.isfile(p_additionalfile) and not p_forcerebuildscenarios:
            return

        self._log.debug("Generating additional xml for %s", p_scenario_name)

        # parameters
        l_length = p_scenarioconfig.get("parameters").get("length")
        l_nbswitches = p_scenarioconfig.get("parameters").get("switches")
        # assume even distributed otl segment lengths
        l_segmentlength = l_length / (l_nbswitches + 1)

        l_additional = optom.common.io.etree.Element("additional")

        # first induction loop at network enter
        optom.common.io.etree.SubElement(
            l_additional,
            "inductionLoop",
            attrib={
                "id": "1_enter",
                "lane": "enter_21start_0",
                "pos": str(
                    self.scenarioconfig.get(p_scenario_name).get("detectorpositions").get("1_enter")
                ),
                "friendlyPos": "true",
                "splitByType": "true",
                "freq": "1",
                "file": p_iloopfile
            }
        )
        # place induction loop right before the first split (i.e. end of starting edge)
        optom.common.io.etree.SubElement(
            l_additional,
            "inductionLoop",
            attrib={
                "id": "2_21segment.0_begin",
                "lane": "enter_21start_0",
                "pos": str(
                    self.scenarioconfig.get(
                        p_scenario_name
                    ).get(
                        "detectorpositions"
                    ).get("2_21segment.0_begin")
                ),
                "friendlyPos": "true",
                "splitByType": "true",
                "freq": "1",
                "file": p_iloopfile
            }
        )

        # induction loops at beginning of each switch
        l_switches = self.scenarioconfig.get(p_scenario_name).get("switchpositions")
        for i, i_switch_pos in list(enumerate(l_switches))[:-1]:
            if i % 2 == 1:
                l_detector_beginning_id = "2_21segment.{}_begin".format(l_switches[i + 1])
                self.scenarioconfig \
                    .get(p_scenario_name) \
                    .get("detectorpositions")[l_detector_beginning_id] = \
                    l_segmentlength + i_switch_pos + l_segmentlength - 5

                l_detector_end_id = "2_21segment.{}_end".format(l_switches[i - 1])
                self.scenarioconfig \
                    .get(p_scenario_name) \
                    .get("detectorpositions")[l_detector_end_id] = \
                    l_segmentlength + i_switch_pos + 5

                optom.common.io.etree.SubElement(
                    l_additional,
                    "inductionLoop",
                    attrib={
                        "id": l_detector_beginning_id,
                        "lane": "21segment.{}_0".format(l_switches[i]),
                        "pos": str(l_segmentlength - 5),
                        "friendlyPos": "true",
                        "splitByType": "true",
                        "freq": "1",
                        "file": p_iloopfile
                    }
                )

                optom.common.io.etree.SubElement(
                    l_additional,
                    "inductionLoop",
                    attrib={
                        "id": l_detector_end_id,
                        "lane": "21segment.{}_0".format(l_switches[i]),
                        "pos": "5",
                        "friendlyPos": "true",
                        "splitByType": "true",
                        "freq": "1",
                        "file": p_iloopfile
                    }
                )

        # induction loop at the end of last one-lane segment and exit
        l_detector_last_id = "2_21segment.{}_end".format(l_switches[-2])
        self.scenarioconfig \
            .get(p_scenario_name) \
            .get("detectorpositions")[l_detector_last_id] = l_length + l_segmentlength

        optom.common.io.etree.SubElement(
            l_additional,
            "inductionLoop",
            attrib={
                "id": "2_21segment.{}_end".format(l_switches[-2]),
                "lane": "21segment.{}_0".format(l_switches[-1]),
                "pos": "5",
                "friendlyPos": "true",
                "splitByType": "true",
                "freq": "1",
                "file": p_iloopfile
            }
        )

        optom.common.io.etree.SubElement(
            l_additional,
            "inductionLoop",
            attrib={
                "id": "3_exit",
                "lane": "21segment.{}_0".format(
                    self.scenarioconfig.get(p_scenario_name).get("switchpositions")[-1]
                ) if l_nbswitches % 2 == 1 or self._onlyoneotlsegment else "21end_exit_0",
                "pos": str(l_segmentlength - 5),
                "friendlyPos": "true",
                "splitByType": "true",
                "freq": "1",
                "file": p_iloopfile
            }
        )
        self.scenarioconfig \
            .get(p_scenario_name) \
            .get("detectorpositions")["3_exit"] = l_length + 2 * l_segmentlength - 5

        with open(p_additionalfile, "w") as f_paddxml:
            f_paddxml.write(optom.common.io.etree.tostring(l_additional, pretty_print=True))

    @staticmethod
    def _generate_config_xml(p_configfile, p_netfile, p_routefile, p_additionalfile, p_settingsfile,
                             p_simtimeinterval, p_forcerebuildscenarios=False):
        """
        Generate SUMO's main configuration file.

        :param p_configfile: Name of scenario (required to id detector positions)
        :param p_netfile: Destination to write network file
        :param p_routefile: Destination to write route file
        :param p_additionalfile: Destination to write additional cfg file
        :param p_settingsfile: Destination to write settings file
        :param p_simtimeinterval: Time interval of simulation
        :param p_forcerebuildscenarios: Rebuild scenarios,
                                        even if they already exist for current run
        """

        if os.path.isfile(p_configfile) and not p_forcerebuildscenarios:
            return
        assert isinstance(p_simtimeinterval, list) and len(p_simtimeinterval) == 2

        l_configuration = optom.common.io.etree.Element("configuration")
        l_input = optom.common.io.etree.SubElement(l_configuration, "input")
        optom.common.io.etree.SubElement(
            l_input,
            "net-file",
            attrib={"value": p_netfile}
        )
        optom.common.io.etree.SubElement(
            l_input,
            "route-files",
            attrib={"value": p_routefile}
        )
        optom.common.io.etree.SubElement(
            l_input,
            "additional-files",
            attrib={"value": p_additionalfile}
        )
        optom.common.io.etree.SubElement(
            l_input,
            "gui-settings-file",
            attrib={"value": p_settingsfile}
        )
        l_time = optom.common.io.etree.SubElement(l_configuration, "time")
        optom.common.io.etree.SubElement(
            l_time,
            "begin",
            attrib={"value": str(p_simtimeinterval[0])}
        )

        with open(p_configfile, "w") as f_pconfigxml:
            f_pconfigxml.write(optom.common.io.etree.tostring(l_configuration, pretty_print=True))

    @staticmethod
    def _generate_settings_xml(
            p_scenarioconfig, p_runcfg, p_settingsfile, p_forcerebuildscenarios=False):
        """
        Generate SUMO's settings configuration file.

        :param p_scenarioconfig: Scenario configuration
        :param p_runcfg: Run configuration
        :param p_settingsfile: Destination to write settings file
        :param p_forcerebuildscenarios: Rebuild scenarios,
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
    def _next_timestep(p_lambda, p_prevstarttime, p_distribution="poisson"):
        """
        Calculate next time step in poission or linear distribution.

        :param p_lambda:
        :param p_prevstarttime:
        :param p_distribution:
        """

        if p_distribution == "poisson":
            return p_prevstarttime + random.expovariate(p_lambda)
        elif p_distribution == "linear":
            return p_prevstarttime + 1 / p_lambda
        else:
            return p_prevstarttime

    def _create_vehicle_distribution(self, p_nbvehicles, p_aadt, p_initialsorting, p_scenario_name):
        """
        Create a distribution of vehicles based on

        :param p_nbvehicles: number of vehicles
        :param p_aadt: anual average daily traffic (vehicles/day/lane)
        :param p_initialsorting: initial sorting of vehicles (by max speed)
                                ["best", "random", "worst"]
        :param p_scenario_name: name of scenario
        """

        assert p_initialsorting in ["best", "random", "worst"]

        l_cfgvtypedistribution = self._runconfig.get("vtypedistribution")
        self._log.debug("Create vehicle distribution with %s", l_cfgvtypedistribution)
        l_vtypedistribution = list(itertools.chain.from_iterable(
            [
                [k] * int(round(100 * v.get("fraction")))
                for (k, v) in l_cfgvtypedistribution.iteritems()
                ]
        ))

        l_vehps = p_aadt / (24 * 60 * 60) \
            if not self._runconfig.get("vehiclespersecond").get("enabled") \
            else self._runconfig.get("vehiclespersecond").get("value")

        l_vehicle_list = [
            optom.environment.vehicle.SUMOVehicle(
                vtype=vtype,
                vtype_sumo_attr=self.vtypesconfig.get(vtype),
                speed_deviation=l_cfgvtypedistribution.get(vtype).get("speedDev"),
                speed_max=min(
                    random.choice(l_cfgvtypedistribution.get(vtype).get("desiredSpeeds")),
                    self.scenarioconfig.get(p_scenario_name).get("parameters").get("speedlimit")
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
            i_vehicle.color = self._speed_colormap(i_vehicle.speed_max)
            # update start time
            i_vehicle.start_time = self._next_timestep(
                l_vehps,
                l_vehicle_list[i - 1].start_time if i > 0 else 0,
                self.runconfig.get("starttimedistribution")
            )
            l_vehicles["vehicle{}".format(i)] = i_vehicle

        return l_vehicles

    def _generate_trip_xml(self, p_scenarioconfig, p_runcfg, p_initialsorting, p_tripfile,
                           p_scenario_name, p_forcerebuildscenarios=False):
        """
        Generate SUMO's trip file.

        :param p_scenarioconfig:
        :param p_runcfg:
        :param p_initialsorting:
        :param p_tripfile:
        :param p_scenario_name:
        :param p_forcerebuildscenarios:
        :return:
        """

        if os.path.isfile(p_tripfile) and not p_forcerebuildscenarios:
            return
        self._log.debug("Generating trip xml for %s", p_scenario_name)
        # generate simple traffic demand by considering AADT, Vmax, roadtype etc
        l_aadt = p_scenarioconfig.get("parameters").get("aadt") \
            if not p_runcfg.get("aadt").get("enabled") else p_runcfg.get("aadt").get("value")

        l_timebegin, l_timeend = p_runcfg.get("simtimeinterval")

        # number of vehicles = AADT / [seconds of day] * [scenario time in seconds]

        l_numberofvehicles = int(round(l_aadt / (24 * 60 * 60) * (l_timeend - l_timebegin))) \
            if not p_runcfg.get("nbvehicles").get("enabled") \
            else p_runcfg.get("nbvehicles").get("value")

        self._log.debug(
            "Scenario's AADT of %d vehicles/average annual day"
            "=> %d vehicles for %d simulation seconds",
            l_aadt, l_numberofvehicles, (l_timeend - l_timebegin)
        )

        l_vehicles = self._create_vehicle_distribution(
            l_numberofvehicles,
            l_aadt,
            p_initialsorting,
            p_scenario_name
        )

        # xml
        l_trips = optom.common.io.etree.Element("trips")

        # create a sumo vtype for each vehicle
        for i_vid, i_vehicle in l_vehicles.iteritems():
            # filter for relevant attributes and transform to string
            l_vattr = i_vehicle.vtype_sumo_attr
            l_vattr["id"] = str(i_vid)
            l_vattr["color"] = "{},{},{},{}".format(*i_vehicle.color)
            # override parameters speedDev, desiredSpeed, and length if defined in run config
            l_runcfgspeeddev = self.runconfig \
                .get("vtypedistribution") \
                .get(l_vattr.get("vClass")) \
                .get("speedDev")
            if l_runcfgspeeddev is not None:
                l_vattr["speedDev"] = str(l_runcfgspeeddev)

            l_runcfgdesiredspeed = self.runconfig \
                .get("vtypedistribution"). \
                get(l_vattr.get("vClass")). \
                get("desiredSpeed")

            l_vattr["speedlimit"] = str(l_runcfgdesiredspeed) \
                if l_runcfgdesiredspeed is not None else str(i_vehicle.speed_max)

            l_runcfglength = self.runconfig \
                .get("vtypedistribution") \
                .get(l_vattr.get("vClass")) \
                .get("length")

            if l_runcfglength is not None:
                l_vattr["length"] = str(l_runcfglength)

            # fix tractor vClass to trailer
            if l_vattr["vClass"] == "tractor":
                l_vattr["vClass"] = "trailer"

            l_vattr["type"] = l_vattr.get("vClass")

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

        :param p_nodefile:
        :param p_edgefile:
        :param p_netfile:
        :param p_forcerebuildscenarios:
        :return:
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

        :param p_netfile:
        :param p_tripfile:
        :param p_routefile:
        :param p_forcerebuildscenarios:
        :return:
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
