import h5py
import numpy as np

class HDFLog(object):

    def __init__(self, p_filename):
        #self._file = h5py.File(p_filename, 'w')
        self._filename = p_filename

    def write(self, p_path, p_objectname, p_object):
        self._file = h5py.File(self._filename, 'w')
        group = self._file.create_group(p_path)
        group.create_dataset(name=p_objectname, data=p_object)
        self._file.flush()
        self._file.close()
