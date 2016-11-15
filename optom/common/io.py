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
import json

import h5py
import yaml

import optom.common.log

try:
    from cjson import encode as jsondumps, decode as jsonloads
except ImportError:
    from json import loads as jsonloads, dumps as jsondumps

try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper

try:
    from lxml import etree
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                except ImportError:
                    print("Failed to import ElementTree from any known place")


class Reader(object):
    """Read xml, json and yaml files."""

    def __init__(self, p_args):
        self._log = optom.common.log.logger(__name__, p_args.loglevel, p_args.logfile)

    def read_etree(self, p_fname):
        """Parses xml file with etree. Returns etree object"""

        self._log.debug("Parsing %s with etree", p_fname)

        return etree.parse(p_fname)

    def read_json(self, p_filename):
        """Reads json file. Returns dictionary."""

        self._log.debug("Reading %s", p_filename)

        with gzip.GzipFile(p_filename, 'r') \
                if p_filename.endswith(".gz") \
                else open(p_filename, mode="r") as f_json:
            l_file = f_json.read()
        return jsonloads(l_file)

    def read_yaml(self, p_filename):
        """
        Reads yaml file and returns dictionary.
        If filename ends with .gz treat file as gzipped yaml.
        """
        self._log.debug("Reading %s", p_filename)

        if p_filename.endswith(".gz"):
            return yaml.load(gzip.GzipFile(p_filename, 'r'), Loader=SafeLoader)
        else:
            return yaml.load(open(p_filename), Loader=SafeLoader)


class Writer(object):
    """Class for writing data to json, yaml, csv, hdf5."""

    def __init__(self, p_args):
        self._log = optom.common.log.logger(__name__, p_args.loglevel, p_args.logfile)

    def write_json_pretty(self, p_object, p_filename):
        """Write json in human readable form (slow!). If filename ends with .gz, compress file."""

        self._log.debug("Writing %s", p_filename)
        f_json = gzip.GzipFile(p_filename, 'w') \
            if p_filename.endswith(".gz") \
            else open(p_filename, mode="w")
        json.dump(p_object, f_json, sort_keys=True, indent=4, separators=(', ', ' : '))
        f_json.close()

    def write_json(self, p_object, p_filename):
        """Write json in compact form, compress file with gzip if filename ends with .gz."""

        self._log.debug("Writing %s", p_filename)
        with gzip.GzipFile(p_filename, 'w') \
                if p_filename.endswith(".gz") \
                else open(p_filename, mode="w") as f_json:
            f_json.write(jsondumps(p_object))

    def write_yaml(self, p_object, p_filename, p_default_flow_style=False):
        """Write yaml, compress file with gzip if filename ends with .gz."""

        self._log.debug("Writing %s", p_filename)
        f_yaml = gzip.GzipFile(p_filename, 'w') \
            if p_filename.endswith(".gz") \
            else open(p_filename, mode="w")
        yaml.dump(p_object, f_yaml, Dumper=SafeDumper, default_flow_style=p_default_flow_style)
        f_yaml.close()

    def write_csv(self, p_fieldnames, p_rowdict, p_filename):
        """Write row dictionary with provided fieldnames as csv with headers."""

        self._log.debug("Writing %s", p_filename)
        with open(p_filename, 'w') as f_csv:
            csv_writer = csv.DictWriter(f_csv, fieldnames=p_fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(p_rowdict)

    def write_hdf5(self, p_filename, p_path, p_objectdict, **kwargs):
        """Write an object to a specific path into an open file, identified by fileid

        Args:
            p_filename: The file name
            p_path: Destination path in HDF5 structure, will be created if not existent.
            p_objectdict: Object(s) to be stored in a named dictionary structure
                          ([name] -> str|int|float|list|numpy)
            **kwargs: Optional arguments passed to create_dataset
        """
        self._log.debug("Writing %s", p_filename)

        # verify whether arguments are sane
        if not isinstance(p_objectdict, dict):
            raise TypeError(u"p_objectdict is not dict")

        f_hdf5 = h5py.File(p_filename, 'a')

        if f_hdf5 and isinstance(f_hdf5, h5py._hl.files.File):

            # create group if it doesn't exist
            l_group = f_hdf5[p_path] if p_path in f_hdf5 else f_hdf5.create_group(p_path)

            # add datasets for each element of p_objectdict,
            # if they already exist by name, overwrite them
            for i_objname, i_objvalue in p_objectdict.items():

                # remove compression if we have a scalar object, i.e. string, int, float
                if isinstance(i_objvalue, (str, int, float)):
                    kwargs.pop("compression", None)
                    kwargs.pop("compression_opts", None)

                if i_objname in l_group:
                    # remove previous object by i_objname id and add the new one
                    del l_group[i_objname]

                l_group.create_dataset(name=i_objname, data=i_objvalue, **kwargs)

        f_hdf5.close()
