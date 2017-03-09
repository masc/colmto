# -*- coding: utf-8 -*-
# @package tests
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of Overtaking Manoeuvres project.   #
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
optom: Test module for common.io.
"""
import json
import tempfile

import optom.common.io
import optom.common.helper

import logging
from lxml import etree
from lxml.etree import XSLT
import yaml
from nose.tools import assert_equals
from nose.tools import assert_true


def test_xslt():
    """Test xslt from io module"""
    l_xslt_template = """<xsl:stylesheet version="1.0"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        </xsl:stylesheet>"""

    assert_true(
        isinstance(
            optom.common.io.xslt(
                etree.XML(
                    l_xslt_template
                )
            ),
            XSLT
        )
    )


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


def test_reader_read_json():
    """Test read_json method from Reader class."""

    l_json_gold = {
        "vehicle56": {
            "timesteps": {
                "981.00": {
                    "lane": "21segment.4080_1",
                    "angle": "90.00",
                    "lanepos": "778.36",
                    "y": "1.65",
                    "x": "6218.36",
                    "speed": "8.25"
                },
                "1322.00": {
                    "lane": "21end_exit_0",
                    "angle": "90.00",
                    "lanepos": "778.48",
                    "y": "-1.65",
                    "x": "8939.98",
                    "speed": "7.28"
                },
                "767.00": {
                    "lane": "21segment.2720_1",
                    "angle": "90.00",
                    "lanepos": "428.48",
                    "y": "1.65",
                    "x": "4508.48",
                    "speed": "8.00"
                },
                "1365.00": {
                    "lane": "21end_exit_0",
                    "angle": "90.00",
                    "lanepos": "1123.24",
                    "y": "-1.65",
                    "x": "9284.74",
                    "speed": "7.64"
                },
                "476.00": {
                    "lane": "enter_21start_0",
                    "angle": "90.00",
                    "lanepos": "409.40",
                    "y": "-1.65",
                    "x": "409.40",
                    "speed": "7.56"
                },
                "1210.00": {
                    "lane": "21segment.5440_1",
                    "angle": "90.00",
                    "lanepos": "1273.80",
                    "y": "1.65",
                    "x": "8073.80",
                    "speed": "11.97"
                }
            }
        }
    }

    f_temp_test = tempfile.NamedTemporaryFile()
    f_temp_test.write(json.dumps(l_json_gold))
    f_temp_test.seek(0)

    args = optom.common.helper.Namespace(
        loglevel=logging.DEBUG, quiet=False, logfile="foo.log"
    )
    l_reader = optom.common.io.Reader(args)

    assert_equals(
        l_reader.read_json(f_temp_test.name),
        l_json_gold
    )

    f_temp_test.close()


def test_reader_read_yaml():
    """Test read_yaml method from Reader class."""

    l_yaml_gold = {
        "vehicle56": {
            "timesteps": {
                "981.00": {
                    "lane": "21segment.4080_1",
                    "angle": "90.00",
                    "lanepos": "778.36",
                    "y": "1.65",
                    "x": "6218.36",
                    "speed": "8.25"
                },
                "1322.00": {
                    "lane": "21end_exit_0",
                    "angle": "90.00",
                    "lanepos": "778.48",
                    "y": "-1.65",
                    "x": "8939.98",
                    "speed": "7.28"
                },
                "767.00": {
                    "lane": "21segment.2720_1",
                    "angle": "90.00",
                    "lanepos": "428.48",
                    "y": "1.65",
                    "x": "4508.48",
                    "speed": "8.00"
                },
                "1365.00": {
                    "lane": "21end_exit_0",
                    "angle": "90.00",
                    "lanepos": "1123.24",
                    "y": "-1.65",
                    "x": "9284.74",
                    "speed": "7.64"
                },
                "476.00": {
                    "lane": "enter_21start_0",
                    "angle": "90.00",
                    "lanepos": "409.40",
                    "y": "-1.65",
                    "x": "409.40",
                    "speed": "7.56"
                },
                "1210.00": {
                    "lane": "21segment.5440_1",
                    "angle": "90.00",
                    "lanepos": "1273.80",
                    "y": "1.65",
                    "x": "8073.80",
                    "speed": "11.97"
                }
            }
        }
    }

    f_temp_test = tempfile.NamedTemporaryFile()
    f_temp_test.write(yaml.dump(l_yaml_gold))
    f_temp_test.seek(0)

    l_reader = optom.common.io.Reader(None)

    assert_equals(
        l_reader.read_yaml(f_temp_test.name),
        l_yaml_gold
    )

    f_temp_test.close()
