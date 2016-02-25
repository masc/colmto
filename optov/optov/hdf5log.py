import h5py

class HDF5Log(object):

    def __init__(self):
        self._file = None

    def open(self, p_filename):
        self._file = h5py.File(p_filename, 'w')

    def write(self, p_path, p_objectname, p_object):
        if type(self._file) is h5py._hl.files.File:
            #TODO: check if group exists before creating it
            group = self._file.create_group(p_path)
            group.create_dataset(name=p_objectname, data=p_object)
            self._file.flush()

    def close(self):
        if type(self._file) is h5py._hl.files.File:
            self._file.close()