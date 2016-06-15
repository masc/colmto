# -*- coding: utf-8 -*-
# @package resultswriter
# @cond LICENSE
# ######################################################################################
# # LGPL License                                                                       #
# #                                                                                    #
# # This file is part of the Optimisation of Overtaking Manoeuvres (OPTOM) project.                     #
# # Copyright (c) 2016, Malte Aschermann (malte.aschermann@tu-clausthal.de)            #
# # This program is free software: you can redistribute it and/or modify               #
# # it under the terms of the GNU Lesser General Public License as                     #
# # published by the Free Software Foundation, either version 3 of the                 #
# # License, or (at your option) any later version.                                    #
# #                                                                                    #
# # This program is distributed in the hope that it will be useful,                    #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of                     #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                      #
# # GNU Lesser General Public License for more details.                                #
# #                                                                                    #
# # You should have received a copy of the GNU Lesser General Public License           #
# # along with this program. If not, see http://www.gnu.org/licenses/                  #
# ######################################################################################
# @endcond

from __future__ import print_function
from __future__ import division
import log
import gzip
import h5py
import yaml
import json

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
    def __init__(self, p_args):
        self._log = log.logger(__name__, p_args.loglevel, p_args.logfile)

    def read_etree(self, p_fname):
        self._log.debug("Parsing %s with etree", p_fname)
        return etree.parse(p_fname)


class Writer(object):

    def __init__(self, p_args):
        self._log = log.logger(__name__, p_args.loglevel, p_args.logfile)

    def write_json_pretty(self, p_object, p_filename):
        self._log.debug("Writing %s", p_filename)
        fp = gzip.GzipFile(p_filename, 'w') if p_filename.endswith(".gz") else open(p_filename, mode="w")
        json.dump(p_object, fp, sort_keys=True, indent=4, separators=(', ', ' : '))
        fp.close()

    def write_json(self, p_object, p_filename):
        self._log.debug("Writing %s", p_filename)
        with gzip.GzipFile(p_filename, 'w') if p_filename.endswith(".gz") else open(p_filename, mode="w") as fp:
            fp.write(jsondumps(p_object))

    def write_yaml(self, p_object, p_filename, p_default_flow_style=False):
        self._log.debug("Writing %s", p_filename)
        fp = gzip.GzipFile(p_filename, 'w') if p_filename.endswith(".gz") else open(p_filename, mode="w")
        yaml.dump(p_object, fp, Dumper=SafeDumper, default_flow_style=p_default_flow_style)
        fp.close()

    ## Write an object to a specific path into an open file, identified by fileid
    #  @param self The object pointer
    #  @param p_filename The file name
    #  @param p_path Destination path in HDF5 structure, will be created if not existent.
    #  @param p_objectdict Object(s) to be stored in a named dictionary structure ([name] -> str|int|float|list|numpy)
    #  @param **kwargs Optional arguments passed to create_dataset
    def write_hdf5(self, p_filename, p_path, p_objectdict, **kwargs):
        # verify whether arguments are sane
        if type(p_objectdict) is not dict:
            raise TypeError(u"p_objectdict is not dict")

        l_file = h5py.File(p_filename, 'a')
        h5py.File

        if l_file and type(l_file) is h5py._hl.files.File:

            # create group if it doesn't exist
            l_group = l_file[p_path] if p_path in l_file else l_file.create_group(p_path)

            # add datasets for each element of p_objectdict, if they already exist by name, overwrite them
            for i_objname,i_objvalue in p_objectdict.items():

                # remove compression if we have a scalar object, i.e. string, int, float
                if type(i_objvalue) in [str, int, float]:
                    kwargs.pop("compression", None)
                    kwargs.pop("compression_opts", None)

                if i_objname in l_group:
                    # remove previous object by i_objname id and add the new one
                    del l_group[i_objname]

                l_group.create_dataset(name=i_objname, data=i_objvalue, **kwargs)

        l_file.close()

