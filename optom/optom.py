# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import os
import shutil
import datetime


class Optom(object):

    def __init__(self):
        l_configdir = os.path.expanduser(u"~/.optom")

        # place default config in ~/.optom if there exists none
        if not os.path.exists(l_configdir):
            os.mkdir(l_configdir)
        if not os.path.isfile(os.path.join(l_configdir, u"runconfig.yaml")):
            shutil.copy("resources/runconfig.yaml",os.path.join(l_configdir, u"runconfig.yaml"))
        if not os.path.isfile(os.path.join(l_configdir, u"vtypesconfig.yaml")):
            shutil.copy("resources/vtypesconfig.yaml",os.path.join(l_configdir, u"vtypesconfig.yaml"))
        if not os.path.isfile(os.path.join(l_configdir, u"scenarioconfig.yaml")):
            shutil.copy("resources/scenarioconfig.yaml",os.path.join(l_configdir, u"scenarioconfig.yaml"))

        l_parser = argparse.ArgumentParser(description="Process parameters for optom")
        l_parser.add_argument("--runconfig", dest="runconfig", type=str, default=os.path.join(l_configdir, u"runconfig.yaml"))
        l_parser.add_argument("--scenarioconfig", dest="scenarioconfig", type=str, default=os.path.join(l_configdir, u"scenarioconfig.yaml"))
        l_parser.add_argument("--vtypesconfig", dest="vtypesconfig", type=str, default=os.path.join(l_configdir, u"vtypesconfig.yaml"))
        l_parser.add_argument("--configdir", dest="configdir", type=str, default=l_configdir)
        l_parser.add_argument("--output-scenario-dir", dest="scenariodir", type=str, default=l_configdir, help="target directory scenario files will be written to")
        l_parser.add_argument("--output-results-dir", dest="resultsdir", type=str, default=l_configdir, help="target directory results will be written to")
        l_parser.add_argument("--scenarios", dest="scenarios", type=str, default=None, nargs="*")
        l_parser.add_argument("--runs", dest="runs", type=int, default=None)
        l_parser.add_argument("--runprefix", dest="runprefix", type=str, default=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        l_parser.add_argument("--logfile", dest="logfile", type=str, default=os.path.join(l_configdir, u"optom.log"))
        l_parser.add_argument("--loglevel", dest="loglevel", type=str, default="INFO")

        l_mutexgrouprunchoice = l_parser.add_mutually_exclusive_group(required=False)
        l_mutexgrouprunchoice.add_argument("--sumo", dest="runsumo", default=False, action="store_true", help="run SUMO simulation")
        l_mutexgrouprunchoice.add_argument("--naive", dest="runnaive", default=False, action="store_true", help="run naive calculation")
        l_mutexgrouprunchoice.add_argument("--mip", dest="runmip", default=False, action="store_true", help="run MIP optimization")
        l_mutexgrouprunchoice.add_argument("--nf", dest="runnf", default=False, action="store_true", help="run network flow optimization")
        l_sumogroup = l_parser.add_argument_group("SUMO")
        l_mutexsumogroup = l_sumogroup.add_mutually_exclusive_group(required=False)
        l_mutexsumogroup.add_argument("--headless", dest="headless", default=None, action="store_true", help="run without SUMO GUI")
        l_mutexsumogroup.add_argument("--gui", dest="gui", default=None, action="store_true", help="run with SUMO GUI")
        l_sumogroup.add_argument("--force-rebuild-scenarios", dest="forcerebuildscenarios", default=False, action="store_true", help="Rebuild and overwrite existing SUMO scenarios in configuration directory ({})".format(l_configdir))
        l_sumogroup.add_argument("--only-one-otl-segment", dest="onlyoneotlsegment", default=False, action="store_true", help="Generate SUMO scenarios with only on OTL segment")
        l_args = l_parser.parse_args()

        if l_args.runsumo:
            from sumo.sumo import Sumo
            l_sumo = Sumo(l_args)
            l_sumo.runScenarios()

if __name__ == "__main__":
    optom = Optom()
