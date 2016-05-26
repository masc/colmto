# -*- coding: utf-8 -*-
# @package configuration
# @cond LICENSE
# ######################################################################################
# # LGPL License                                                                       #
# #                                                                                    #
# # This file is part of the Optimisation of Overtaking Manoeuvres (OPTOM) project.                     #
# # Copyright (c) 2016, Malte Aschermann (malte.aschermann@tu-clausthal.de)            #
# # This program is free software: you can redistribute it and/or modify               #
# # it under the terms of the GNU Lesser General Public License as                     #
# # published by the Free Software Foundation, either version 3 of the                 #
# # License, or (at your option) any later version.                                    #
# #                                                                                    #
# # This program is distributed in the hope that it will be useful,                    #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of                     #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                      #
# # GNU Lesser General Public License for more details.                                #
# #                                                                                    #
# # You should have received a copy of the GNU Lesser General Public License           #
# # along with this program. If not, see http://www.gnu.org/licenses/                  #
# ######################################################################################
# @endcond
from __future__ import print_function
from __future__ import division

try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper
import yaml
import os
import sh

from optom.common import log


class Configuration(object):

    def __init__(self, p_args):
        self._log = log.logger(__name__, p_args.loglevel, p_args.logfile)

        self._args = p_args

        if p_args.runconfig is None:
            raise BaseException("run configuration flag is None")

        if p_args.scenarioconfig is None:
            raise BaseException("scenario configuration flag is None")

        if p_args.vtypesconfig is None:
            raise BaseException("vtype configuration flag is None")

        if not os.path.isfile(p_args.runconfig):
            raise BaseException("run configuration {} is not a file".format(p_args.runconfig))

        if not os.path.isfile(p_args.scenarioconfig):
            raise BaseException("scenario configuration {} is not a file".format(p_args.scenarioconfig))

        if not os.path.isfile(p_args.vtypesconfig):
            raise BaseException("vtype configuration {} is not a file".format(p_args.vtypesconfig))

        self._outputdir = p_args.outputdir
        self._scenariodir = p_args.scenariodir
        self._runconfig = yaml.load(open(p_args.runconfig), Loader=SafeLoader)
        self._scenarioconfig = yaml.load(open(p_args.scenarioconfig), Loader=SafeLoader)
        self._vtypesconfig = yaml.load(open(p_args.vtypesconfig), Loader=SafeLoader)
        self._runprefix = p_args.runprefix
        # store currently running version
        # inferred from current HEAD if located inside a git project. otherwise set version to "UNKNOWN"
        try:
            self._optomversion = str(sh.git.bake("rev-parse")("HEAD")).replace("\n","")
        except sh.ErrorReturnCode:
            self._optomversion = "UNKNOWN"

        self._overrideCfgFlags(p_args)

    def _overrideCfgFlags(self, p_args):
        if p_args.headless:
            self._runconfig.get("sumo")["headless"] = True
        if p_args.gui:
            self._runconfig.get("sumo")["headless"] = False
        if p_args.runs is not None:
            self._runconfig["runs"] = p_args.runs
        if p_args.scenarios is not None:
            self._runconfig["scenarios"] = p_args.scenarios if p_args.scenarios != ["all"] else self._scenarioconfig.keys()

    @property
    def runconfig(self):
        return self._runconfig

    @property
    def scenarioconfig(self):
        return self._scenarioconfig

    @property
    def vtypesconfig(self):
        return self._vtypesconfig

    @property
    def outputdir(self):
        return self._outputdir

    @property
    def runprefix(self):
        return self._runprefix


