# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import sys,os
from sumo.sumo import Sumo
from common.configuration import Configuration

class Optov(object):

    def __init__(self):
        l_configdir = os.path.expanduser(u"~/.optov")
        if not os.path.exists(l_configdir):
            os.mkdir(l_configdir)

        l_parser = argparse.ArgumentParser(description="Process parameters for optov")
        l_parser.add_argument("--runconfig", dest="runconfig", type=str, default=os.path.join(l_configdir, u"runconfig.json"))
        l_parser.add_argument("--roadwayconfig", dest="roadwayconfig", type=str, default=os.path.join(l_configdir, u"roadwayconfig.json"))
        l_parser.add_argument("--configdir", dest="configdir", type=str, default=l_configdir)

        l_mutexgrouprunchoice = l_parser.add_mutually_exclusive_group(required=True)
        l_mutexgrouprunchoice.add_argument("--sumo", dest="runsumo", default=False, action='store_true', help="run SUMO simulation")
        l_mutexgrouprunchoice.add_argument("--naive", dest="runnaive", default=False, action='store_true', help="run naive calculation")
        l_mutexgrouprunchoice.add_argument("--mip", dest="runmip", default=False, action='store_true', help="run MIP optimization")
        l_mutexgrouprunchoice.add_argument("--nf", dest="runnf", default=False, action='store_true', help="run network flow optimization")
        l_args = l_parser.parse_args()

        l_configuration = Configuration(l_args)
        if l_args.runsumo:
            l_sumo = Sumo(l_configuration)
            l_sumo.runAllScenarios()


if __name__ == "__main__":
    optov = Optov()
