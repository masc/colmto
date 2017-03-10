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
import logging
import gzip

import optom.common.io
import optom.common.helper

import h5py
# pylint: disable=no-name-in-module
from lxml import etree
from lxml.etree import XSLT
# pylint: enable=no-name-in-module
import yaml
from nose.tools import assert_equals
from nose.tools import assert_true
from nose.tools import assert_raises


def test_xslt():
    """Test xslt from io module"""
    l_xslt_template = """<xsl:stylesheet version="1.0"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        </xsl:stylesheet>"""

    assert_true(
        isinstance(
            optom.common.io.xslt(
                # pylint: disable=no-member
                etree.XML(
                    l_xslt_template
                )
                # pylint: enable=no-member
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

    for i_elements in zip(
            optom.common.io.Reader(None).read_etree(f_temp_test.name).iter(),
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

    assert_equals(
        optom.common.io.Reader(args).read_json(f_temp_test.name),
        l_json_gold
    )

    f_temp_test.close()

    # gzip
    f_temp_test = tempfile.NamedTemporaryFile(suffix=".gz")
    f_gz = gzip.GzipFile(f_temp_test.name, "a")
    f_gz.write(yaml.dump(l_json_gold))
    f_gz.close()
    f_temp_test.seek(0)

    assert_equals(
        optom.common.io.Reader(None).read_yaml(f_temp_test.name),
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

    assert_equals(
        optom.common.io.Reader(None).read_yaml(f_temp_test.name),
        l_yaml_gold
    )

    f_temp_test.close()

    # gzip
    f_temp_test = tempfile.NamedTemporaryFile(suffix=".gz")
    f_gz = gzip.GzipFile(f_temp_test.name, "a")
    f_gz.write(yaml.dump(l_yaml_gold))
    f_gz.close()
    f_temp_test.seek(0)

    assert_equals(
        optom.common.io.Reader(None).read_yaml(f_temp_test.name),
        l_yaml_gold
    )
    f_temp_test.close()


def test_write_yaml():
    """Test write_yaml method from Writer class."""
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

    args = optom.common.helper.Namespace(
        loglevel="debug", quiet=False, logfile="foo.log"
    )
    optom.common.io.Writer(args).write_yaml(l_yaml_gold, f_temp_test.name)
    f_temp_test.seek(0)

    assert_equals(
        yaml.safe_load(f_temp_test),
        l_yaml_gold
    )

    f_temp_test.close()

    # gzip
    f_temp_test = tempfile.NamedTemporaryFile(suffix=".gz")
    optom.common.io.Writer(None).write_yaml(l_yaml_gold, f_temp_test.name)
    f_temp_test.seek(0)

    assert_equals(
        yaml.safe_load(gzip.GzipFile(f_temp_test.name, "r")),
        l_yaml_gold
    )
    f_temp_test.close()


def test_write_json():
    """Test write_json method from Writer class."""
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

    args = optom.common.helper.Namespace(
        loglevel=logging.DEBUG, quiet=False, logfile="foo.log"
    )
    f_temp_test = tempfile.NamedTemporaryFile()
    optom.common.io.Writer(args).write_json(l_json_gold, f_temp_test.name)
    f_temp_test.seek(0)

    assert_equals(
        json.load(f_temp_test),
        l_json_gold
    )

    f_temp_test.close()

    # gzip
    f_temp_test = tempfile.NamedTemporaryFile(suffix=".gz")
    optom.common.io.Writer(None).write_json(l_json_gold, f_temp_test.name)
    f_temp_test.seek(0)

    assert_equals(
        json.load(gzip.GzipFile(f_temp_test.name, "r")),
        l_json_gold
    )
    f_temp_test.close()

    # test write.json_pretty
    f_temp_test = tempfile.NamedTemporaryFile()
    optom.common.io.Writer(None).write_json_pretty(l_json_gold, f_temp_test.name)
    f_temp_test.seek(0)

    assert_equals(
        json.load(f_temp_test),
        l_json_gold
    )

    f_temp_test.close()

    # gzip
    f_temp_test = tempfile.NamedTemporaryFile(suffix=".gz")
    optom.common.io.Writer(None).write_json_pretty(l_json_gold, f_temp_test.name)
    f_temp_test.seek(0)

    assert_equals(
        json.load(gzip.GzipFile(f_temp_test.name, "r")),
        l_json_gold
    )
    f_temp_test.close()


def test_flatten_object_dict():
    """test flatten_object_dict"""
    l_test_dict = {
        "foo": {
            "baz": {
                "value": 23,
                "attr": "baz"
            }
        },
        "bar": {
            "bar": {
                "value": 42,
                "attr": "bar"
            }
        },
        "baz": {
            "foo": {
                "value": 21,
                "attr": "foo"
            }
        }
    }
    l_gold_dict = {
        "foo/baz": {
            "value": 23,
            "attr": "baz"
        },
        "bar/bar": {
            "value": 42,
            "attr": "bar"
        },
        "baz/foo": {
            "value": 21,
            "attr": "foo"
        }
    }

    assert_equals(
        # pylint: disable=protected-access
        optom.common.io.Writer(None)._flatten_object_dict(l_test_dict),
        # pylint: enable=protected-access
        l_gold_dict
    )


def test_write_csv():
    """test write_csv"""
    f_temp_test = tempfile.NamedTemporaryFile()
    optom.common.io.Writer(None).write_csv(
        ["foo", "bar"],
        [{"foo": 1, "bar": 1}, {"foo": 2, "bar": 2}],
        f_temp_test.name
    )
    f_temp_test.seek(0)

    with f_temp_test as csv_file:
        assert_equals(
            "".join(csv_file.readlines()),
            "foo,bar\r\n1,1\r\n2,2\r\n"
        )

    f_temp_test.close()


def test_write_hdf5():
    """test write_hdf5"""
    l_obj_dict = {
        "foo/baz": {
            "value": 23,
            "attr": "baz"
        },
        "bar/bar": {
            "value": 42,
            "attr": "bar"
        },
        "baz/foo": {
            "value": 21,
            "attr": "foo"
        }
    }

    f_temp_test = tempfile.NamedTemporaryFile(suffix=".hdf5")

    optom.common.io.Writer(None).write_hdf5(
        object_dict=l_obj_dict,
        hdf5_file=f_temp_test.name,
        hdf5_base_path="root"
    )
    f_temp_test.seek(0)
    l_hdf = h5py.File(f_temp_test.name, "r")
    l_test_dict = {}
    l_hdf["root"].visititems(
        lambda key, value: l_test_dict.update({key: value.value})
        if isinstance(value, h5py.Dataset) else None
    )
    l_hdf.close()
    assert_equals(
        l_test_dict,
        {u'bar/bar': 42, u'baz/foo': 21, u'foo/baz': 23}
    )

    optom.common.io.Writer(None).write_hdf5(
        object_dict={
            "foo/baz": {
                "value": 11,
                "attr": {"info": "meh"}
            }
        },
        hdf5_file=f_temp_test.name,
        hdf5_base_path="root"
    )

    l_hdf = h5py.File(f_temp_test.name, "r")
    l_test_dict = {}
    assert_equals(
        l_hdf["root/foo/baz"].value,
        11
    )
    assert_equals(
        l_hdf["root/foo/baz"].attrs.get("info"),
        "meh"
    )
    l_hdf.close()

    # test for exceptions
    with assert_raises(TypeError):
        optom.common.io.Writer(None).write_hdf5(
            object_dict="foo",
            hdf5_file=f_temp_test.name,
            hdf5_base_path="root"
        )

    with assert_raises(IOError):
        optom.common.io.Writer(None).write_hdf5(
            object_dict=l_obj_dict,
            hdf5_file="{}/".format(f_temp_test.name),
            hdf5_base_path="root"
        )

    with assert_raises(TypeError):
        optom.common.io.Writer(None).write_hdf5(
            object_dict={
                "foo/baz": {
                    "value": lambda x: x,
                    "attr": {"info": "meh"}
                }
            },
            hdf5_file=f_temp_test.name,
            hdf5_base_path="root"
        )
