from __future__ import print_function

import argparse
import sys,os
from sumo.runtime import runtime as sumoruntime


class Optov(object):

    def __init__(self):
        l_configdir = os.path.expanduser(u"~/.optov")
        l_parser = argparse.ArgumentParser(description="Process parameters for optov")
        l_parser.add_argument("--config", dest="config", type=str, default=os.path.join(l_configdir, u"config.json"))
        l_mutexgrouprunchoice = l_parser.add_mutually_exclusive_group(required=True)
        l_mutexgrouprunchoice.add_argument("--sumo", dest="runsumo", default=False, action='store_true', help="start SUMO simulation")
        l_mutexgrouprunchoice.add_argument("--naive", dest="runnaive", default=False, action='store_true', help="start naive simulation")
        l_args = l_parser.parse_args()
        print(l_args)

if __name__ == "__main__":
    optov = Optov()
