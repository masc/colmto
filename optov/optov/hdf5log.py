from __future__ import print_function
import h5py
import sys

class HDF5Log(object):

    def __init__(self):
        self._fileids = {}

    def open(self, p_filename, p_mode="a"):
        try:
            l_file = h5py.File(p_filename, p_mode)
            self._fileids[l_file.fid.id] = l_file
            return l_file.fid.id
        except IOError:
            print(u"Exception while trying to open file %s with mode %s", (p_filename, p_mode))

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

    def writeOnce(self, p_filename, p_path, p_objectdict, p_mode="a", **kwargs):
        l_fileid = self.open(p_filename, p_mode)
        self.write(l_fileid, p_path, p_objectdict, **kwargs)
        self.close(l_fileid)

    def close(self, p_fileid):
        l_file = self._fileids[p_fileid]
        if l_file and type(l_file) is h5py._hl.files.File:
            l_file.flush()
            l_file.close()
        del self._fileids[p_fileid]


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




