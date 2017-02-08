# -*- coding: utf-8 -*-
# @package tests
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
"""
optom: Test module for environment.cse.
"""
from nose.tools import assert_is_instance

import optom.cse.cse


def test_base_cse():
    """
    Test BaseCSE class
    """
    l_base_cse = optom.cse.cse.BaseCSE()
    assert_is_instance(l_base_cse, optom.cse.cse.BaseCSE)


def test_sumo_cse():
    """
    Test SumoCSE class
    """
    l_sumo_cse = optom.cse.cse.SumoCSE()
    assert_is_instance(l_sumo_cse, optom.cse.cse.SumoCSE)
