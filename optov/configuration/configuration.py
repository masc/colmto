# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import os
import yaml

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
        self._runconfig = yaml.safe_load(open(p_args.runconfig))
        self._scenarioconfig = yaml.safe_load(open(p_args.scenarioconfig))
        self._vtypesconfig = yaml.safe_load(open(p_args.vtypesconfig))




    def write(self, p_config, p_location):
        fp = open(p_location, "w")
        yaml.safe_dump(p_config, fp)
        fp.close()

    def getRunConfig(self):
        return self._runconfig

    def getScenarioConfig(self):
        return self._scenarioconfig

    def getVtypesConfig(self):
        return self._vtypesconfig

    def getConfigDir(self):
        return self._configdir


