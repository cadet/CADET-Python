#Python 3.5+
#Depends on addict  https://github.com/mewwts/addict
#Depends on h5py, numpy

from addict import Dict

import h5py
import types
import numpy
import subprocess
import pprint
import time
import copy

class Cadet():

    #cadet_path must be set in order for simulations to run
    cadet_path = None

    pp = pprint.PrettyPrinter(indent=4)

    def __init__(self, *data):
        self.root = Dict()
        for i in data:
            self.root.update(copy.deepcopy(i))

    def load(self):
        with h5py.File(self.filename, 'r') as h5file:
            self.root = Dict(recursively_load(h5file, '/'))

    def save(self):
        with h5py.File(self.filename, 'w') as h5file:
            recursively_save(h5file, '/', self.root)

    def run(self, timeout = None):
        if self.cadet_path is not None:
            subprocess.run([self.cadet_path, self.filename], timeout = timeout)
        else:
            import sys
            sys.exit("cadet_path is None and must be set to the path where cadet-cli is located in order to run simulations")

    def __str__(self):
        temp = []
        temp.append('Filename = %s' % self.filename)
        temp.append(self.pp.pformat(self.root))
        return '\n'.join(temp)

    def update(self, merge):
        self.root.update(merge.root)

    def __getitem__(self, key):
        key = key.lower()
        obj = self.root
        for i in key.split('/'):
            if i:
                obj = obj[i]
        return obj

    def __setitem__(self, key, value):
        key = key.lower()
        obj = self.root
        parts = key.split('/')
        for i in parts[:-1]:
            if i:
                obj = obj[i]
        obj[parts[-1]] = value

def recursively_load( h5file, path): 

    ans = {}
    for key, item in h5file[path].items():
        key = key.lower()
        if isinstance(item, h5py._hl.dataset.Dataset):
            ans[key] = item.value
        elif isinstance(item, h5py._hl.group.Group):
            ans[key] = recursively_load(h5file, path + key + '/')
    return ans 

def recursively_save( h5file, path, dic):

    # argument type checking
    if not isinstance(dic, dict):
        raise ValueError("must provide a dictionary")        

    if not isinstance(path, str):
        raise ValueError("path must be a string")
    if not isinstance(h5file, h5py._hl.files.File):
        raise ValueError("must be an open h5py file")
    # save items to the hdf5 file
    for key, item in dic.items():
        key = str(key)
        if not isinstance(key, str):
            raise ValueError("dict keys must be strings to save to hdf5")
        #handle   int, float, string and ndarray of int32, int64, float64
        if isinstance(item, str):
            h5file[path + key.upper()] = numpy.array(item, dtype='S' + str(len(item)+1))
        
        elif isinstance(item, int):
            h5file[path + key.upper()] = numpy.array(item, dtype=numpy.int32)
        
        elif isinstance(item, float):
            h5file[path + key.upper()] = numpy.array(item, dtype=numpy.float64)
        
        elif isinstance(item, numpy.ndarray) and item.dtype == numpy.float64:
            h5file[path + key.upper()] = item
        
        elif isinstance(item, numpy.ndarray) and item.dtype == numpy.float32:
            h5file[path + key.upper()] = numpy.array(item, dtype=numpy.float64)
        
        elif isinstance(item, numpy.ndarray) and item.dtype == numpy.int32:
            h5file[path + key.upper()] = item
        
        elif isinstance(item, numpy.ndarray) and item.dtype == numpy.int64:
            h5file[path + key.upper()] = item.astype(numpy.int32)
        
        elif isinstance(item, list) and all(isinstance(i, int) for i in item):
            h5file[path + key.upper()] = numpy.array(item, dtype=numpy.int32)
        
        elif isinstance(item, list) and any(isinstance(i, float) for i in item):
            h5file[path + key.upper()] = numpy.array(item, dtype=numpy.float64)
        
        elif isinstance(item, numpy.int32):
            h5file[path + key.upper()] = item
        
        elif isinstance(item, numpy.float64):
            h5file[path + key.upper()] = item

        elif isinstance(item, numpy.float32):
            h5file[path + key.upper()] = numpy.array(item, dtype=numpy.float64)
        
        elif isinstance(item, numpy.bytes_):
            h5file[path + key.upper()] = item
        
        elif isinstance(item, bytes):
            h5file[path + key.upper()] = item

        # save dictionaries
        elif isinstance(item, dict):
            recursively_save(h5file, path + key + '/', item)
        # other types cannot be saved and will result in an error
        else:
            #print(item)
            raise ValueError('Cannot save %s type.' % type(item))




