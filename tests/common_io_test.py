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
optom: Test module for common.io.
"""
import tempfile

from nose.tools import assert_equals

import optom.common.io


def test_reader_read_etree():
    """Test read_etree method from Reader class."""

    l_xml_string = """
        <fcd-export xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/fcd_file.xsd">
            <timestep time="0.00">
                <vehicle id="vehicle0" x="4.40" y="0.05" angle="90.00" type="vehicle0"
                speed="27.78" pos="4.40" lane="enter_21start_0" slope="0.00"/>
            </timestep>
            <timestep time="1.00">
                <vehicle id="vehicle0" x="30.89" y="0.05" angle="90.00" type="vehicle0"
                speed="26.49" pos="30.89" lane="enter_21start_0" slope="0.00"/>
            </timestep>
            <timestep time="2.00">
                <vehicle id="vehicle0" x="57.63" y="0.05" angle="90.00" type="vehicle0"
                speed="26.75" pos="57.63" lane="enter_21start_0" slope="0.00"/>
            </timestep>
        </fcd-export>
        """

    f_temp_gold = tempfile.NamedTemporaryFile()
    f_temp_gold.write(l_xml_string)
    f_temp_gold.seek(0)

    f_temp_test = tempfile.NamedTemporaryFile()
    f_temp_test.write(l_xml_string)
    f_temp_test.seek(0)

    l_reader = optom.common.io.Reader(None)

    for i_elements in zip(
            l_reader.read_etree(f_temp_test.name).iter(),
            optom.common.io.etree.parse(f_temp_gold.name).iter()):
        assert_equals(
            i_elements[0].items(),
            i_elements[1].items()
        )

    f_temp_gold.close()
    f_temp_test.close()
