# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import os
import yaml
try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper

class Configuration(object):

    def __init__(self, p_args):
        if p_args.runconfig == None:
            raise BaseException("run configuration flag is None")

        if p_args.scenarioconfig == None:
            raise BaseException("scenario configuration flag is None")

        if p_args.vtypesconfig == None:
            raise BaseException("vtype configuration flag is None")

        if not os.path.isfile(p_args.runconfig):
            raise BaseException("run configuration {} is not a file".format(p_args.runconfig))

        if not os.path.isfile(p_args.scenarioconfig):
            raise BaseException("scenario configuration {} is not a file".format(p_args.scenarioconfig))

        if not os.path.isfile(p_args.vtypesconfig):
                    raise BaseException("vtype configuration {} is not a file".format(p_args.vtypesconfig))

        self._configdir = p_args.configdir
        self._runconfig = yaml.load(open(p_args.runconfig), Loader=SafeLoader)
        self._scenarioconfig = yaml.load(open(p_args.scenarioconfig), Loader=SafeLoader)
        self._vtypesconfig = yaml.load(open(p_args.vtypesconfig), Loader=SafeLoader)

        self._overrideCfgFlags(p_args)

    def _overrideCfgFlags(self, p_args):
        if p_args.headless == True:
            self.getRunConfig().get("sumo")["headless"] = True
        if p_args.gui == True:
            self.getRunConfig().get("sumo")["headless"] = False
        if p_args.runs != None:
            self.getRunConfig()["runs"] = p_args.runs
        if p_args.scenarios != None:
            self.getRunConfig()["scenarios"] = p_args.scenarios if p_args.scenarios != ["all"] else self.getScenarioConfig().keys()

    def write(self, p_config, p_location):
        fp = open(p_location, "w")
        yaml.dump(p_config, fp, Dumper=SafeDumper, default_flow_style=False)
        fp.close()

    def getRunConfig(self):
        return self._runconfig

    def getScenarioConfig(self):
        return self._scenarioconfig

    def getVtypesConfig(self):
        return self._vtypesconfig

    def getConfigDir(self):
        return self._configdir


