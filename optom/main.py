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
# pylint: disable=too-few-public-methods
"""Optom main module."""
import argparse
import datetime
import os
import shutil
import sys

import optom.common.configuration
import optom.common.log
import optom.sumo.sumosim


class Optom(object):
    """Optom main class"""

    def __init__(self):
        l_config_dir = os.path.expanduser(u"~/.optom")

        l_parser = argparse.ArgumentParser(description="Process parameters for optom")
        l_parser.add_argument(
            "--runconfigfile", dest="runconfigfile", type=str,
            default=os.path.join(l_config_dir, u"runconfig.yaml")
        )
        l_parser.add_argument(
            "--scenarioconfigfile", dest="scenarioconfigfile", type=str,
            default=os.path.join(l_config_dir, u"scenarioconfig.yaml")
        )
        l_parser.add_argument(
            "--vtypesconfigfile", dest="vtypesconfigfile", type=str,
            default=os.path.join(l_config_dir, u"vtypesconfig.yaml")
        )
        l_parser.add_argument(
            "--fresh-configs",
            dest="freshconfigs",
            action="store_true",
            default=False,
            help="generate fresh config files (overwrite existing ones in {})".format(l_config_dir)
        )
        l_parser.add_argument(
            "--output-dir", dest="output_dir", type=str,
            default=l_config_dir
        )
        l_parser.add_argument(
            "--output-scenario-dir", dest="scenario_dir", type=str,
            default=l_config_dir, help="target directory scenario files will be written to"
        )
        l_parser.add_argument(
            "--output-results-dir", dest="results_dir", type=str,
            default=l_config_dir, help="target directory results will be written to"
        )
        l_parser.add_argument(
            "--scenarios", dest="scenarios", type=str, nargs="*",
            default=None
        )
        l_parser.add_argument(
            "--runs", dest="runs", type=int,
            default=None
        )
        l_parser.add_argument(
            "--run_prefix", dest="run_prefix", type=str,
            default=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        )
        l_parser.add_argument(
            "--logfile", dest="logfile", type=str,
            default=os.path.join(l_config_dir, u"optom.log")
        )
        l_parser.add_argument(
            "--loglevel", dest="loglevel", type=str,
            default="INFO"
        )
        l_parser.add_argument(
            "-q", "--quiet", dest="quiet", action="store_true",
            default=False, help="suppress log info output to stdout"
        )

        l_mutexgrouprunchoice = l_parser.add_mutually_exclusive_group(required=False)
        l_mutexgrouprunchoice.add_argument(
            "--sumo", dest="runsumo", action="store_true",
            default=False, help="run SUMO simulation"
        )

        l_sumogroup = l_parser.add_argument_group("SUMO")

        l_sumogroup.add_argument(
            "--cse", dest="cse_enabled", action="store_true",
            default=None, help="run SUMO simulation with central optimisation entity (CSE)"
        )

        l_mutexsumogroup = l_sumogroup.add_mutually_exclusive_group(required=False)
        l_mutexsumogroup.add_argument(
            "--headless", dest="headless", action="store_true",
            default=None, help="run without SUMO GUI"
        )
        l_mutexsumogroup.add_argument(
            "--gui", dest="gui", action="store_true",
            default=None, help="run with SUMO GUI"
        )
        l_sumogroup.add_argument(
            "--force-rebuild-scenarios", dest="forcerebuildscenarios", action="store_true",
            default=False,
            help="Rebuild and overwrite existing SUMO scenarios in configuration directory "
                 "({})".format(l_config_dir)
        )
        l_sumogroup.add_argument(
            "--only-one-otl-segment", dest="onlyoneotlsegment", action="store_true",
            default=False, help="Generate SUMO scenarios with only on OTL segment"
        )
        self._args = l_parser.parse_args()

        # place default config in ~/.optom if there exists none or --fresh-configs set
        if not os.path.exists(l_config_dir):
            os.mkdir(l_config_dir)
        l_cwd = os.path.realpath(os.path.dirname(sys.argv[0]))
        if not os.path.isfile(
                os.path.join(l_config_dir, u"runconfig.yaml")) or self._args.freshconfigs:
            shutil.copy(
                os.path.join(l_cwd, "optom/resources/runconfig.yaml"),
                os.path.join(l_config_dir, u"runconfig.yaml")
            )
        if not os.path.isfile(
                os.path.join(l_config_dir, u"vtypesconfig.yaml")) or self._args.freshconfigs:
            shutil.copy(
                os.path.join(l_cwd, "optom/resources/vtypesconfig.yaml"),
                os.path.join(l_config_dir, u"vtypesconfig.yaml")
            )
        if not os.path.isfile(
                os.path.join(l_config_dir, u"scenarioconfig.yaml")) or self._args.freshconfigs:
            shutil.copy(
                os.path.join(l_cwd, "optom/resources/scenarioconfig.yaml"),
                os.path.join(l_config_dir, u"scenarioconfig.yaml")
            )

        self._log = optom.common.log.logger(
            __name__,
            self._args.loglevel,
            self._args.quiet,
            self._args.logfile
        )

    def run(self):
        """Run OPTOM"""
        self._log.info("---- Starting OPTOM ----")
        l_configuration = optom.common.configuration.Configuration(self._args)
        self._log.debug("Initial loading of configuration done")

        if l_configuration.run_config.get("sumo").get("enabled") or self._args.runsumo:
            self._log.info("---- Starting SUMO Baseline Simulation ----")
            optom.sumo.sumosim.SumoSim(self._args).run_scenarios()
