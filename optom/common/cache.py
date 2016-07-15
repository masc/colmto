# -*- coding: utf-8 -*-
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

