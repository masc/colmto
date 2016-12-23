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
from nose.tools import assert_equal
from nose.tools import assert_is_instance

import optom.environment.cse


def test_base_cse():
    """
    Test BaseCSE class
    """
    l_base_cse = optom.environment.cse.BaseCSE()
    assert_is_instance(l_base_cse.whitelist, frozenset)
    assert_equal(len(l_base_cse.whitelist), 0)
    l_base_cse.allow("vehicle0")
    l_base_cse.allow("vehicle1").allow("vehicle2")
    assert_equal(l_base_cse.whitelist, frozenset(("vehicle0", "vehicle1", "vehicle2")))
    l_base_cse.deny("vehicle1")
    assert_equal(l_base_cse.whitelist, frozenset(("vehicle0", "vehicle2")))
    l_base_cse.deny("vehicle2").allow("vehicle3")
    assert_equal(l_base_cse.whitelist, frozenset(("vehicle0", "vehicle3")))
    l_base_cse.clear().allow("vehicle5")
    assert_equal(l_base_cse.whitelist, frozenset(("vehicle5",)))


def test_sumo_cse():
    """
    Test SumoCSE class
    """
    l_sumo_cse = optom.environment.cse.SumoCSE()
    assert_is_instance(l_sumo_cse.whitelist, frozenset)
    assert_equal(len(l_sumo_cse.whitelist), 0)
    l_sumo_cse.allow("vehicle0")
    l_sumo_cse.allow("vehicle1").allow("vehicle2")
    assert_equal(l_sumo_cse.whitelist, frozenset(("vehicle0", "vehicle1", "vehicle2")))
    l_sumo_cse.deny("vehicle1")
    assert_equal(l_sumo_cse.whitelist, frozenset(("vehicle0", "vehicle2")))
    l_sumo_cse.deny("vehicle2").allow("vehicle3")
    assert_equal(l_sumo_cse.whitelist, frozenset(("vehicle0", "vehicle3")))
    l_sumo_cse.clear().allow("vehicle5")
    assert_equal(l_sumo_cse.whitelist, frozenset(("vehicle5",)))
