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
"""I/O module"""
from __future__ import division
from __future__ import print_function

import csv
import gzip

try:
    from cjson import encode as jsondumps, decode as jsonloads
except ImportError:
    from json import loads as jsonloads, dumps as jsondumps

import json


try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper

import yaml

import h5py

try:
    from lxml import etree
    from lxml.etree import XSLT
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
        from xml.etree import XSLT
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
            from xml.etree import XSLT
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
                from xml.etree import XSLT
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                    from xml.etree import XSLT
                except ImportError:
                    print("Failed to import ElementTree from any known place")

import optom.common.log


def xslt(template):
    """
    Wrapper to apply template to XSLT and return transformation object.
    Args:
        template: XSLT template
    Returns:
        transformation object
    """
    return XSLT(template)


class Reader(object):
    """Read xml, json and yaml files."""

    def __init__(self, args):
        """C'tor."""
        if args is not None:
            self._log = optom.common.log.logger(__name__, args.loglevel, args.quiet, args.logfile)
        else:
            self._log = optom.common.log.logger(__name__)

    def read_etree(self, fname):
        """Parses xml file with etree. Returns etree object"""

        self._log.debug("Parsing %s with etree", fname)

        return etree.parse(fname)

    def read_json(self, filename):
        """Reads json file. Returns dictionary."""

        self._log.debug("Reading %s", filename)

        with gzip.GzipFile(filename, 'r') \
                if filename.endswith(".gz") \
                else open(filename, mode="r") as f_json:
            l_file = f_json.read()
        return jsonloads(l_file)

    def read_yaml(self, filename):
        """
        Reads yaml file and returns dictionary.
        If filename ends with .gz treat file as gzipped yaml.
        """
        self._log.debug("Reading %s", filename)

        if filename.endswith(".gz"):
            return yaml.load(gzip.GzipFile(filename, 'r'), Loader=SafeLoader)
        else:
            return yaml.load(open(filename), Loader=SafeLoader)


class Writer(object):
    """Class for writing data to json, yaml, csv, hdf5."""

    def __init__(self, args):
        if args is not None:
            self._log = optom.common.log.logger(__name__, args.loglevel, args.quiet, args.logfile)
        else:
            self._log = optom.common.log.logger(__name__)

    def write_json_pretty(self, object, filename):
        """Write json in human readable form (slow!). If filename ends with .gz, compress file."""

        self._log.debug("Writing %s", filename)
        f_json = gzip.GzipFile(filename, 'w') \
            if filename.endswith(".gz") \
            else open(filename, mode="w")
        json.dump(object, f_json, sort_keys=True, indent=4, separators=(', ', ' : '))
        f_json.close()

    def write_json(self, object, filename):
        """Write json in compact form, compress file with gzip if filename ends with .gz."""

        self._log.debug("Writing %s", filename)
        with gzip.GzipFile(filename, 'w') \
                if filename.endswith(".gz") \
                else open(filename, mode="w") as f_json:
            f_json.write(jsondumps(object))

    def write_yaml(self, object, filename, default_flow_style=False):
        """Write yaml, compress file with gzip if filename ends with .gz."""

        self._log.debug("Writing %s", filename)
        f_yaml = gzip.GzipFile(filename, 'w') \
            if filename.endswith(".gz") \
            else open(filename, mode="w")
        yaml.dump(object, f_yaml, Dumper=SafeDumper, default_flow_style=default_flow_style)
        f_yaml.close()

    def write_csv(self, fieldnames, rowdict, filename):
        """Write row dictionary with provided fieldnames as csv with headers."""

        self._log.debug("Writing %s", filename)
        with open(filename, 'w') as f_csv:
            csv_writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(rowdict)

    def write_hdf5(self, filename, path, objectdict, **kwargs):
        """Write an object to a specific path into an open file, identified by fileid

        Args:
            filename: The file name
            path: Destination path in HDF5 structure, will be created if not existent.
            objectdict: Object(s) to be stored in a named dictionary structure
                          ([name] -> str|int|float|list|numpy)
            **kwargs: Optional arguments passed to create_dataset
        """
        self._log.debug("Writing %s", filename)

        # verify whether arguments are sane
        if not isinstance(objectdict, dict):
            raise TypeError(u"objectdict is not parameters")

        f_hdf5 = h5py.File(filename, 'a')

        if not f_hdf5 and not isinstance(f_hdf5, h5py.File):
            raise Exception

        # create group if it doesn't exist
        l_group = f_hdf5[path] if path in f_hdf5 else f_hdf5.create_group(path)

        # add datasets for each element of objectdict,
        # if they already exist by name, overwrite them
        for i_objname, i_objvalue in objectdict.items():

            # remove compression if we have a scalar object, i.e. string, int, float
            if isinstance(i_objvalue, (str, int, float)):
                kwargs.pop("compression", None)
                kwargs.pop("compression_opts", None)

            if i_objname in l_group:
                # remove previous object by i_objname id and add the new one
                del l_group[i_objname]

            l_group.create_dataset(name=i_objname, data=i_objvalue, **kwargs)

        f_hdf5.close()
