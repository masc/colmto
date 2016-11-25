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
"""Configuration super class."""
from __future__ import division
from __future__ import print_function

import copy
import os

import sh

from optom.common import log
from optom.common.io import Reader


class Configuration(object):
    """Configuration reads OPTOM's general cfg files."""

    @property
    def args(self):
        """Return config command line arguments."""
        return self._args

    @property
    def runconfig(self):
        """Return run config."""
        return self._runconfig

    @property
    def scenarioconfig(self):
        """Return scenario config."""
        return self._scenarioconfig

    @property
    def scenariodir(self):
        """Return scenario directory."""
        return self._args.scenariodir

    @property
    def vtypesconfig(self):
        """Return vehicle type config."""
        return self._vtypesconfig

    @property
    def outputdir(self):
        """Return destination dir."""
        return self._args.outputdir

    @property
    def runprefix(self):
        """Return run prefix."""
        return self._args.runprefix

    @property
    def optom_version(self):
        """Return optom version"""
        return self._optom_version

    def __init__(self, p_args):
        """
        C'tor: Read scenario/run/vtype configs and merge with command line arguments.
        Command line args override cfgs.
        """

        self._log = log.logger(__name__, p_args.loglevel, p_args.logfile)
        self._reader = Reader(p_args)
        self._args = copy.deepcopy(p_args)

        if self._args.runconfigfile is None:
            raise BaseException("run configuration file flag is None")

        if self._args.scenarioconfigfile is None:
            raise BaseException("scenario configuration file flag is None")

        if self._args.vtypesconfigfile is None:
            raise BaseException("vtype configuration file flag is None")

        if not os.path.isfile(self._args.runconfigfile):
            raise BaseException("run configuration {} is not a file".format(self.runconfig))

        if not os.path.isfile(self._args.scenarioconfigfile):
            raise BaseException(
                "scenario configuration {} is not a file".format(self._args.scenarioconfigfile)
            )

        if not os.path.isfile(self._args.vtypesconfigfile):
            raise BaseException(
                "vtype configuration {} is not a file".format(self._args.vtypesconfigfile)
            )

        self._runconfig = self._reader.read_yaml(self._args.runconfigfile)
        self._scenarioconfig = self._reader.read_yaml(self._args.scenarioconfigfile)
        self._vtypesconfig = self._reader.read_yaml(self._args.vtypesconfigfile)

        # store currently running version
        # inferred from current HEAD if located inside a git project.
        # otherwise set version to "UNKNOWN"
        try:
            l_git_commit_id = sh.Command("git")(["rev-parse", "HEAD"])
            self._optom_version = str(l_git_commit_id).replace("\n", "")
        except sh.ErrorReturnCode:
            self._optom_version = "UNKNOWN"
        except sh.CommandNotFound:
            self._log.debug("Git command not found in PATH. Setting commit id to UNKNOWN.")
            self._optom_version = "UNKNOWN"

        self._override_cfg_flags()

    def _override_cfg_flags(self):
        """Override the cfs flags."""

        if self.args.headless:
            self.runconfig.get("sumo")["headless"] = True
        if self.args.gui:
            self.runconfig.get("sumo")["headless"] = False
        if self.args.runs is not None:
            self.runconfig["runs"] = self._args.runs
        if self.args.scenarios is not None:
            if self.args.scenarios != ["all"]:
                self.runconfig["scenarios"] = self.args.scenarios
            else:
                self.scenarioconfig.keys()
