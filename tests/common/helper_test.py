# -*- coding: utf-8 -*-
# @package tests
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Cooperative Lane Management and Traffic flow     #
# # Optimisation project.                                                     #
# # Copyright (c) 2017, Malte Aschermann (malte.aschermann@tu-clausthal.de)   #
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
colmto: Test module for common.helper.
"""
import colmto.common.helper
from nose.tools import assert_equal


def test_enum():
    """
    Test enum
    """
    l_enum = colmto.common.helper.Enum(["foo", "bar", "baz"])
    assert_equal(l_enum.foo, 0)
    assert_equal(l_enum.bar, 1)
    assert_equal(l_enum.baz, 2)


def test_namespace():
    """
    Test namespace
    """
    # pylint: disable=no-member
    l_namespace = colmto.common.helper.Namespace(foo=0, bar=1, baz=2)
    assert_equal(l_namespace.foo, 0)
    assert_equal(l_namespace.bar, 1)
    assert_equal(l_namespace.baz, 2)
    # pylint: enable=no-member
