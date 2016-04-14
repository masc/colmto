# -*- coding: utf-8 -*-
from __future__ import print_function
from common.sumocfg import SumoConfig

class Sumo(object):

    def __init__(self, p_args):
        self._sumocfg = SumoConfig(p_args)
