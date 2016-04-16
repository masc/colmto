# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

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
            "maxSpeed" : 120/3.6, # maximal allowed speed in m/s
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
            "maxSpeed" : 100/3.6,
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
            "maxSpeed" : 100/3.6,
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
        "vtypes" : {
            "passenger" : {
                "length" : 4.3,
                "width" : 1.8,
                "height" : 1.5,
                "minGap" : 2.5,
                "accel" : 2.9,
                "decel" : 7.5,
                "maxSpeed" : 180 / 3.6,
                "speedFactor": 1,
                "speedDev" : 0.1,
                "dspeedbucket": {
                    "min": 130/3.6,
                    "max": 250/3.6
                }
            },
            "van" : {
                "length" : 4.7,
                "width" : 1.9,
                "height" : 1.73,
                "minGap" : 2.5,
                "accel" : 2.9,
                "decel" : 7.5,
                "maxSpeed" : 180 / 3.6,
                "speedFactor": 1,
                "speedDev" : 0.1,
                "dspeedbucket": {
                    "min": 100/3.6,
                    "max": 130/3.6
                }
            },
            "delivery" : {
                "length" : 6.5,
                "width" : 2.16,
                "height" : 2.86,
                "minGap" : 2.5,
                "accel" : 2.9,
                "decel" : 7.5,
                "maxSpeed" : 180 / 3.6,
                "speedFactor": 1,
                "speedDev" : 0.1,
                "dspeedbucket": {
                    "min": 80/3.6,
                    "max": 100/3.6
                }
            },
            "truck" : {
                "length" : 7.1,
                "width" : 2.4,
                "height" : 2.4,
                "minGap" : 2.5,
                "accel" : 1.3,
                "decel" : 4.0,
                "maxSpeed" : 130 / 3.6,
                "speedFactor": 1,
                "speedDev" : 0.1,
                "dspeedbucket": {
                    "min": 70/3.6,
                    "max": 80/3.6
                }
            },
            "heavytransport" : {
                "length" : 7.1,
                "width" : 2.4,
                "height" : 2.4,
                "minGap" : 2.5,
                "accel" : 1.3,
                "decel" : 4.0,
                "maxSpeed" : 40 / 3.6,
                "speedFactor": 1,
                "speedDev" : 0.1,
                "dspeedbucket": {
                    "min": 30/3.6,
                    "max": 70/3.6
                }
            },
            "tractor" : {
                "length" : 3.0,
                "width" : 2.4,
                "height" : 2.4,
                "minGap" : 2.5,
                "accel" : 1.3,
                "decel" : 4.0,
                "maxSpeed" : 30 / 3.6,
                "speedFactor": 1,
                "speedDev" : 0.1,
                "dspeedbucket": {
                    "min": 0,
                    "max": 30/3.6
                }
            }
        },
        "gui-delay" : 200,
        "desiredspeeds" : {
            "distribution" : "GAUSS",
            "args" : [90/3.6, 30/3.6] # Gauss: [mu, sigma]
        }
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


