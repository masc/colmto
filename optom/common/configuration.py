# -*- coding: utf-8 -*-
# @package optom
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of Overtaking Manoeuvres project.   #
# # Copyright (c) 2016, Malte Aschermann (malte.aschermann@tu-clausthal.de)   #
# # This program is free software: you can redistribute it and/or modify      #
# # it under the terms of the GNU Lesser General Public License as            #
# # published by the Free Software Foundation, either version 3 of the        #
# # License, or (at your option) any later version.                           #
# #                                                                           #
# # This program is distributed in the hope that it will be useful,           #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# # GNU Lesser General Public License for more details.                       #
# #                                                                           #
# # You should have received a copy of the GNU Lesser General Public License  #
# # along with this program. If not, see http://www.gnu.org/licenses/         #
# #############################################################################
# @endcond
"""Configuration super class."""
from __future__ import division
from __future__ import print_function

import copy
import os

import sh

import optom.common.io
import optom.common.log


_DEFAULT_CONFIG_RUN = {
    "aadt": {
        "enabled": False,
        "value": 13000
    },
    "cse-enabled": False,
    "initialsortings": ["random"],
    "nbvehicles": {
        "enabled": False,
        "value": 30
    },
    "runs": 1,
    "scenarios": ["NI-B210"],
    "simtimeinterval": [0, 1800],
    "starttimedistribution": "poisson",
    # "policies": [
    #     {
    #         "type": "SUMOSpeedPolicy",
    #         "behaviour": "deny",
    #         "args": {
    #             "speed_range": (0., 30/3.6)
    #         }
    #     },
    #     {
    #         "type": "SUMOPositionPolicy",
    #         "behaviour": "deny",
    #         "args": {
    #             "position_bbox": ((1350., -2.), (2500., 2.))
    #         },
    #         "vehicle_policies": {
    #             "rule": "any",
    #             "policies": [
    #                 {
    #                     "type": "SUMOSpeedPolicy",
    #                     "behaviour": "deny",
    #                     "args": {
    #                         "speed_range": (0., 85/3.6)
    #                     },
    #                 }
    #             ]
    #         }
    #     }
    # ],
    "sumo": {
        "enabled": True,
        "gui-delay": 200,
        "headless": True,
        "port": 8873
    },
    "vehiclespersecond": {
        "enabled": False,
        "value": 0.5
    },
    "vtypedistribution": {
        "passenger": {
            "desiredSpeeds": [34.0],
            "fraction": 0.5,
            "speedDev": 0.0
        },
        "tractor": {
            "desiredSpeeds": [8.0],
            "fraction": 0.2,
            "speedDev": 0.0
        },
        "truck": {
            "desiredSpeeds": [23.0],
            "fraction": 0.3,
            "speedDev": 0.0
        }
    }
}

_DEFAULT_CONFIG_SCENARIO = {
    "NI-B210": {
        "description": {
            "from": "OUJever",
            "road": "B210",
            "state": "NI",
            "to": "OUJever"
        },
        "parameters": {
            "aadt": 13000.0,
            "detectorpositions": [0, 1360, 2720, 4080, 5440],
            "length": 6800.0,
            "speedlimit": 27.77777777777778,
            "switches": 4,
            "switchpositions": [0, 1360, 2720, 4080, 5440]
        },
        "baseline_relative_time_loss": {
            "passenger": 0.0,
            "truck": 0.0,
            "tractor": 0.0,
        }
    },
    "HE-B62": {
        "description": {
            "from": "Coelbe",
            "road": "B62",
            "state": "HE",
            "to": "Kirchhain"
        },
        "parameters": {
            "aadt": 13000.0,
            "detectorpositions": [0, 1171, 2342, 3513, 4684, 5855, 7026, 8197],
            "length": 8200.0,
            "speedlimit": 27.77777777777778,
            "switches": 6,
            "switchpositions": [0, 1171, 2342, 3513, 4684, 5855, 7026, 8197]
        }
    },
    "NW-B1": {
        "description": {
            "from": "Paderborn",
            "road": "B1",
            "state": "NW",
            "to": "Schlangen"
        },
        "parameters": {
            "aadt": 17000.0,
            "detectorpositions": [0, 977, 1954, 2931, 3908, 4885, 5862, 6839, 7816, 8793],
            "length": 8800.0,
            "speedlimit": 27.77777777777778,
            "switches": 8,
            "switchpositions": [0, 977, 1954, 2931, 3908, 4885, 5862, 6839, 7816, 8793]
        }
    },
    "HE-B49": {
        "description": {
            "from": "Leun",
            "road": "B49",
            "state": "HE",
            "to": "Niederbiel"
        },
        "parameters": {
            "aadt": 19000.0,
            "detectorpositions": [0, 900, 1800, 2700, 3600],
            "length": 4500.0,
            "speedlimit": 27.77777777777778,
            "switches": 4,
            "switchpositions": [0, 900, 1800, 2700, 3600]
        }
    },
    "BY-B20": {
        "description": {
            "from": "Cham",
            "road": "B20",
            "state": "BY",
            "to": "Straubing"
        },
        "parameters": {
            "aadt": 20000.0,
            "detectorpositions": [0, 1375, 2750, 4125, 5500, 6875, 8250, 9625],
            "length": 11000.0,
            "speedlimit": 27.77777777777778,
            "switches": 7,
            "switchpositions": [0, 1375, 2750, 4125, 5500, 6875, 8250, 9625]
        }
    },
    "BY-B471": {
        "description": {
            "from": "OUDachau",
            "road": "B471",
            "state": "BY",
            "to": "OUDachau"
        },
        "parameters": {
            "aadt": 16000.0,
            "detectorpositions": [0, 1280, 2560, 3840, 5120],
            "length": 6400.0,
            "speedlimit": 27.77777777777778,
            "switches": 4,
            "switchpositions": [0, 1280, 2560, 3840, 5120]
        }
    }
}

_DEFAULT_CONFIG_VTYPES = {
    "delivery": {
        "accel": 2.9,
        "decel": 7.5,
        "height": 2.86,
        "length": 6.5,
        "maxSpeed": 50.0,
        "minGap": 2.5,
        "speedDev": 0.1,
        "speedFactor": 1,
        "vClass": "custom2",
        "vType": "delivery",
        "width": 2.16,
        "dsat_threshold": 0.2
    },
    "heavytransport": {
        "accel": 1.3,
        "decel": 4.0,
        "height": 2.4,
        "length": 7.1,
        "maxSpeed": 11.11111111111111,
        "minGap": 2.5,
        "speedDev": 0.1,
        "speedFactor": 1,
        "vClass": "custom2",
        "vType": "trailer",
        "width": 2.4,
        "dsat_threshold": 0.2
    },
    "passenger": {
        "accel": 2.9,
        "decel": 7.5,
        "height": 1.5,
        "length": 4.3,
        "maxSpeed": 50.0,
        "minGap": 2.5,
        "speedDev": 0.1,
        "speedFactor": 1,
        "vClass": "custom2",
        "vType": "passenger",
        "width": 1.8,
        "dsat_threshold": 0.2
    },
    "tractor": {
        "accel": 1.3,
        "decel": 4.0,
        "height": 2.4,
        "length": 3.0,
        "maxSpeed": 8.333333333333334,
        "minGap": 2.5,
        "speedDev": 0.1,
        "speedFactor": 1,
        "vClass": "custom2",
        "vType": "tractor",
        "width": 2.4,
        "dsat_threshold": 1.0
    },
    "truck": {
        "accel": 1.3,
        "decel": 4.0,
        "height": 2.4,
        "length": 7.1,
        "maxSpeed": 36.11111111111111,
        "minGap": 2.5,
        "speedDev": 0.1,
        "speedFactor": 1,
        "vClass": "custom2",
        "vType": "truck",
        "width": 2.4,
        "dsat_threshold": 0.1
    },
    "van": {
        "accel": 2.9,
        "decel": 7.5,
        "height": 1.73,
        "length": 4.7,
        "maxSpeed": 50.0,
        "minGap": 2.5,
        "speedDev": 0.1,
        "speedFactor": 1,
        "vClass": "custom2",
        "vType": "delivery",
        "width": 1.9,
        "dsat_threshold": 0.2
    }
}


class Configuration(object):
    """Configuration reads OPTOM's general cfg files."""

    def __init__(self, args):
        """
        C'tor: Read scenario/run/vehicle_type configs and merge with command line arguments.
        Command line args override cfgs.
        """

        self._log = optom.common.log.logger(__name__, args.loglevel, args.quiet, args.logfile)
        self._reader = optom.common.io.Reader(args)
        self._writer = optom.common.io.Writer(args)
        self._args = args

        if self._args.runconfigfile is None:
            raise BaseException("run configuration file flag is None")

        if self._args.scenarioconfigfile is None:
            raise BaseException("scenario configuration file flag is None")

        if self._args.vtypesconfigfile is None:
            raise BaseException("vehicle_type configuration file flag is None")

        if not os.path.isfile(self._args.runconfigfile) or self._args.freshconfigs:
            self._log.info(
                "generating default run configuration %s", self._args.runconfigfile
            )
            self._run_config = copy.copy(_DEFAULT_CONFIG_RUN)
            self._writer.write_yaml(self._run_config, self._args.runconfigfile)
        else:
            self._run_config = self._reader.read_yaml(self._args.runconfigfile)

        if not os.path.isfile(self._args.scenarioconfigfile) or self._args.freshconfigs:
            self._log.info(
                "generating default scenario configuration %s", self._args.scenarioconfigfile
            )
            self._scenario_config = copy.copy(_DEFAULT_CONFIG_SCENARIO)
            self._writer.write_yaml(self._scenario_config, self._args.scenarioconfigfile)
        else:
            self._scenario_config = self._reader.read_yaml(self._args.scenarioconfigfile)

        if not os.path.isfile(self._args.vtypesconfigfile) or self._args.freshconfigs:
            self._log.info(
                "generating default vehicle_type configuration %s", self._args.vtypesconfigfile
            )
            self._vtypes_config = copy.copy(_DEFAULT_CONFIG_VTYPES)
            self._writer.write_yaml(self._vtypes_config, self._args.vtypesconfigfile)
        else:
            self._vtypes_config = self._reader.read_yaml(self._args.vtypesconfigfile)

        # store currently running version
        # inferred from current HEAD if located inside a git project.
        # otherwise set version to "UNKNOWN"
        try:
            l_git_commit_id = sh.Command("git")(["rev-parse", "HEAD"])
            self._run_config["optom_version"] = str(l_git_commit_id).replace("\n", "")
        except sh.ErrorReturnCode:
            self._run_config["optom_version"] = "UNKNOWN"
        except sh.CommandNotFound:
            self._log.debug("Git command not found in PATH. Setting commit id to UNKNOWN.")
            self._run_config["optom_version"] = "UNKNOWN"

        self._override_cfg_flags()

    def _override_cfg_flags(self):
        """Override the cfs flags."""

        if self._args.headless:
            self._run_config.get("sumo")["headless"] = True
        if self._args.gui:
            self._run_config.get("sumo")["headless"] = False
        if self._args.cse_enabled:
            self._run_config["cse-enabled"] = True
        if self._args.runs is not None:
            self._run_config["runs"] = self._args.runs
        if self._args.scenarios is not None:
            if self._args.scenarios != ["all"]:
                self._run_config["scenarios"] = self._args.scenarios
            else:
                self._run_config["scenarios"] = self._scenario_config.keys()

    @property
    def run_config(self):
        """
        @retval run config
        """
        return copy.copy(self._run_config)

    @property
    def scenario_config(self):
        """
        @retval scenario config
        """
        return copy.copy(self._scenario_config)

    @property
    def scenario_dir(self):
        """
        @retval scenario directory.
        """
        return copy.copy(self._args.scenario_dir)

    @property
    def vtypes_config(self):
        """
        @retval vehicle type config
        """
        return copy.copy(self._vtypes_config)

    @property
    def output_dir(self):
        """
        @retval destination dir
        """
        return copy.copy(self._args.output_dir)

    @property
    def run_prefix(self):
        """
        @retval run prefix
        """
        return copy.copy(self._args.run_prefix)
