from __future__ import print_function
import h5py

## @package hd5flog
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


class HDF5Log(object):

    ## Constructor initializing an empty dictionary for concurrently open files
    def __init__(self):
        self._fileids = {}

    ## Open a hdf5 file
    #  @param self The object pointer
    #  @param p_filename The file name as a string
    #  @param p_mode The mode this file will be opened (Optional, default "a")
    #  @return unique file id, received from OS
    def open(self, p_filename, p_mode="a"):
        try:
            l_file = h5py.File(p_filename, p_mode)
            self._fileids[l_file.fid.id] = l_file
            return l_file.fid.id
        except IOError:
            print(u"Exception while trying to open file %s with mode %s", (p_filename, p_mode))

    ## Write an object to a specific path into an open file, identified by fileid
    #  Will overwrite existing objects in HDF5 path, will not flush or close file afterwards. (Intended for frequent data logs to same file)
    #  @param self The object pointer
    #  @param p_fileid The file id, obtained by open()
    #  @param p_path Destination path in HDF5 structure, will be created if not existent.
    #  @param p_objectdict Object(s) to be stored in a named dictionary structure ([name] -> str|int|float|list|numpy object)
    #  @param **kwargs Optional arguments passed to create_dataset
    def write(self, p_fileid, p_path, p_objectdict, **kwargs):
        # verify whether arguments are sane
        if type(p_fileid) is not int:
            raise TypeError(u"p_fileid is not int")
        if type(p_path) is not type(u""): # python 2 vs 3 fix
            raise TypeError(u"p_path is not str/unicode")
        if type(p_objectdict) is not dict:
            raise TypeError(u"p_objectdict is not dict")

        l_file = self._fileids[p_fileid]

        if l_file and type(l_file) is h5py._hl.files.File:

            # create group if it doesn't exist
            if p_path in l_file:
                l_group = l_file[p_path]
            else:
                l_group = l_file.create_group(p_path)

            # add datasets for each element of p_objectdict, if they already exist by name, overwrite them
            for i_objname,i_objvalue in p_objectdict.items():

                # remove compression if we have a scalar object, i.e. string, int, float
                if type(i_objname) in [type(u""),  int, float]:
                    kwargs.pop("compression", None)
                    kwargs.pop("compression_opts", None)

                if i_objname in l_group:
                    # remove previous object by i_objname id and add the new one
                    del l_group[i_objname]

                l_group.create_dataset(name=i_objname, data=i_objvalue, **kwargs)

    ## Write an object to a specific path into a file.
    #  Same functionality as write(), but does not need an previously open file. Flushes and closes file afterwards.
    #  @param self The object pointer
    #  @param p_filename The file name as a string
    #  @param p_path Destination path in HDF5 structure, will be created if not existent.
    #  @param p_objectdict Object(s) to be stored in a named dictionary structure ([name] -> str|int|float|list|numpy object)
    #  @param **kwargs Optional arguments passed to create_dataset
    def writeOnce(self, p_filename, p_path, p_objectdict, p_mode="a", **kwargs):
        l_fileid = self.open(p_filename, p_mode)
        self.write(l_fileid, p_path, p_objectdict, **kwargs)
        self.close(l_fileid)

    ## Closes an open file, identified by p_fileid
    #  @param self The object pointer
    #  @param p_fileid The file id, obtained by open()
    def close(self, p_fileid):
        l_file = self._fileids[p_fileid]
        if l_file and type(l_file) is h5py._hl.files.File:
            l_file.flush()
            l_file.close()
        del self._fileids[p_fileid]

    ## Flushes an open file, identified by p_fileid
    #  @param self The object pointer
    #  @param p_fileid The file id, obtained by open()
    def flush(self, p_fileid):
        l_file = self._fileids[p_fileid]
        if l_file and type(l_file) is h5py._hl.files.File:
            l_file.flush()


if __name__ == "__main__":
    print(u"demo mode:")
    from random import randint
    hdf5log = HDF5Log()
    l_fileid = hdf5log.open(u"test_longwrite.hdf5")
    for i_runid in range(100):
        for i_vid in range(10):
            l_origin = (randint(0,20), randint(0,20))
            l_destination = (randint(0,20), randint(0,20))

            l_object = {u"name" : u"car%d" % (i_vid),
                        u"origin" : l_origin,
                        u"destination" : l_destination,
                        u"route" : [l_origin] + [(randint(0,20),randint(0,20)) for i in range(randint(10,30))] + [l_destination] }
            hdf5log.write(l_fileid, u"run%d/vehicle%d/" % (i_runid, i_vid), l_object, compression="gzip", compression_opts=9)
            l_vehiclename = u"test_vehicle_%d.hdf5" % (i_vid)
            hdf5log.writeOnce(l_vehiclename, u"/", l_object, compression="gzip", compression_opts=9)
    hdf5log.close(l_fileid)

    print("printing structure of test_longwrite.hdf5 run0 (fist 10 elements):")

    l_file = h5py.File("test_longwrite.hdf5", mode="r")
    l_items = []
    l_file[u"run0"].visititems(lambda name, obj: l_items.append((name,obj)))
    for i_name, i_obj in l_items[:10]:
        print(i_name,i_obj)
    l_file.close()
