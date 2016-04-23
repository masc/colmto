# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import os
import yaml

class Configuration(object):

    def __init__(self, p_args):
        if p_args.runconfig == None:
            raise BaseException("run configuration flag is None")

        if p_args.roadwayconfig == None:
            raise BaseException("roadway configuration flag is None")

        if not os.path.isfile(p_args.runconfig):
            raise BaseException("run configuration {} is not a file".format(p_args.runconfig))

        if not os.path.isfile(p_args.roadwayconfig):
            raise BaseException("roadway configuration {} is not a file".format(p_args.roadwayconfig))

        self._configdir = p_args.configdir

        self._runconfig = yaml.safe_load(open(p_args.runconfig))

        self._roadwayconfig = yaml.safe_load(open(p_args.roadwayconfig))

        if p_args.headless != None:
            self._runconfig.get("sumo")["headless"] = p_args.headless



    def write(self, p_config, p_location):
        fp = open(p_location, "w")
        yaml.safe_dump(p_config, fp)
        fp.close()

    def getRunConfig(self):
        return self._runconfig

    def getRoadwayConfig(self):
        return self._roadwayconfig

    def getConfigDir(self):
        return self._configdir


