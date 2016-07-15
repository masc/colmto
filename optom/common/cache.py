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
from __future__ import print_function
from __future__ import division

try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper

try:
    from cjson import encode as jsondumps, decode as jsonloads
except ImportError:
    from json import loads as jsonloads, dumps as jsondumps

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

import yaml
import gzip
import os


class Cache(object):

    def __init__(self):
        self._filecache = {}

    @property
    def filecache(self):
        return self._filecache

    def cachefile(self, p_fname):
        if not os.path.isfile(p_fname):
            return

        if p_fname.endswith(".yaml"):
            self._filecache[p_fname] = yaml.load(open(p_fname).read(), Loader=SafeLoader)
        if p_fname.endswith(".yaml.gz"):
            self._filecache[p_fname] = yaml.load(gzip.GzipFile(p_fname).read(), Loader=SafeLoader)
        if p_fname.endswith(".json"):
            self._filecache[p_fname] = jsonloads(open(p_fname).read())
        if p_fname.endswith(".json.gz"):
            self._filecache[p_fname] = jsonloads(gzip.GzipFile(p_fname).read())
        if p_fname.endswith(".xml"):
            self._filecache[p_fname] = ElementTree.parse(p_fname)
        if p_fname.endswith(".xml.gz"):
            self._filecache[p_fname] = ElementTree.parse(gzip.GzipFile(p_fname).read())

        return self._filecache.get(p_fname)
