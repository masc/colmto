# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import json
import gzip
import h5py

# @package resultswriter
# @cond LICENSE
# ######################################################################################
# # LGPL License                                                                       #
# #                                                                                    #
# # This file is part of the Optimized Overtaking (optov) project.                     #
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


class ResultsWriter(object):

    def writeJsonCompact(self, p_object, p_filename):
        self._writeJson(p_object, p_filename, p_sort_keys=True, p_indent=None, p_separators=(',', ':'))

    def writeJson(self, p_object, p_filename):
        self._writeJson(p_object, p_filename, p_sort_keys=True, p_indent=4, p_separators=(', ', ' : '))

    def _writeJson(self, p_object, p_filename, **p_jsonargs):
        if p_filename.endswith(".gz"):
            fp = gzip.GzipFile(p_filename, 'w')
        else:
            fp = open(p_filename, mode="w")

        print(" * writing {}".format(p_filename))
        json.dump(p_object, fp, p_jsonargs)
        fp.close()
        print("   done")

    ## Write an object to a specific path into an open file, identified by fileid
    #  @param self The object pointer
    #  @param p_filename The file name
    #  @param p_path Destination path in HDF5 structure, will be created if not existent.
    #  @param p_objectdict Object(s) to be stored in a named dictionary structure ([name] -> str|int|float|list|numpy)
    #  @param **kwargs Optional arguments passed to create_dataset
    def writeHDF5(self, p_filename, p_path, p_objectdict, **kwargs):
        # verify whether arguments are sane
        if type(p_objectdict) is not dict:
            raise TypeError(u"p_objectdict is not dict")

        l_file = h5py.File(p_filename, 'a')

        if l_file and type(l_file) is h5py._hl.files.File:

            # create group if it doesn't exist
            if p_path in l_file:
                l_group = l_file[p_path]
            else:
                l_group = l_file.create_group(p_path)

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