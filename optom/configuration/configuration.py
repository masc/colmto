# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper
import yaml
import os

from common import log


class Configuration(object):

    def __init__(self, p_args):
        self._log = log.logger(p_args, __name__)

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

        self._configdir = p_args.configdir
        self._scenariodir = p_args.scenariodir
        self._runconfig = yaml.load(open(p_args.runconfig), Loader=SafeLoader)
        self._scenarioconfig = yaml.load(open(p_args.scenarioconfig), Loader=SafeLoader)
        self._vtypesconfig = yaml.load(open(p_args.vtypesconfig), Loader=SafeLoader)

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

    def write(self, p_config, p_location):
        fp = open(p_location, "w")
        yaml.dump(p_config, fp, Dumper=SafeDumper, default_flow_style=False)
        fp.close()

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
    def configdir(self):
        return self._configdir


