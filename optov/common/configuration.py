# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import json
import copy

defaultroadwayconfig = {
    # roadway parameters taken from [Irzik 2009, A1] (limited to ones with given DTV)
    "BW-B31n-Stockach-Ueberlingen" : {
        "description" : {
            "state" : "BW",
            "road" : "B31n",
            "from" : "Stockach",
            "to" : "Ueberlingen"
        },
        "parameters" : {
            "length" : 10.0 * 1000, # length in meter
            "aadt" : 12700, # Annual average daily traffic
            "vmax" : 120/3.6, # maximal allowed speed in m/s
            "type" : "TLE", # Two-Lane Expressway (Kraftfahrstraße) or General Traffic (Allg. Verkehr)
            "switches" : 4
        }
    },
    "BW-B33-Gengenbach-Biberach" : {
        "description" : {
            "state" : "BW",
            "road" : "B33",
            "from" : "Gengenbach",
            "to" : "Biberach"
        },
        "parameters" : {
            "length" : 5.6*1000,
            "aadt" : 18000,
            "vmax" : 100/3.6,
            "type" : "TLE",
            "switches" : 4
        }
    },
    "BW-B292-Aglasterhausen-Obrigheim" : {
        "description" : {
            "state" : "BW",
            "road" : "B292",
            "from" : "Aglasterhausen",
            "to" : "Obrigheim"
        },
        "parameters" : {
            "length" : 7.8*1000,
            "aadt" : 12870,
            "vmax" : 100/3.6,
            "type" : "GT",
            "switches" : 8
        }
    },
}

defaultrunconfig = {
    "sumo" : {
        "time" : {
            "begin" : 0,
            "end" : 60*60
        },
        "delay" : 200,
        "bunches" : [
            {
                "vehicles" : 10,
                "desiredspeeds" : {
                    "distribution" : "MANUAL",
                    "args" : [80, 90, 70, 50, 90, 100, 120, 70, 85, 30]
                },
                "starttime" : 0
            },
            {
                "vehicles" : 10,
                "desiredspeeds" : {
                    "distribution" : "GAUSS",
                    "args" : [85, 20] # Gauss: [mu, sigma]
                },
                "starttime" : 60
            }
        ]
    }
}


class Configuration(object):

    def __init__(self, p_args):
        if p_args.runconfig == None:
            raise BaseException("run configuration flag is None")

        if p_args.roadwayconfig == None:
            raise BaseException("roadway configuration flag is None")

        self._configdir = p_args.configdir

        if os.path.isfile(p_args.runconfig):
            self._runconfig = json.load(open(p_args.runconfig))
        else:
            self._runconfig = copy.deepcopy(defaultrunconfig)
            self.write(self._runconfig, p_args.runconfig)

        if os.path.isfile(p_args.roadwayconfig):
            self._roadwayconfig = json.load(open(p_args.roadwayconfig))
        else:
            self._roadwayconfig = copy.deepcopy(defaultroadwayconfig)
            self.write(self._roadwayconfig, p_args.roadwayconfig)

    def write(self, p_config, p_location):
        fp = open(p_location, mode="w")
        json.dump(p_config, fp, sort_keys=True, indent=4, separators=(',', ' : '))
        fp.close()

    def getRunConfig(self):
        return self._runconfig

    def getRoadwayConfig(self):
        return self._roadwayconfig

    def getConfigDir(self):
        return self._configdir


