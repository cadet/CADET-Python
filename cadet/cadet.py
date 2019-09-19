from addict import Dict

import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=FutureWarning)
    import h5py
import numpy
import subprocess
import pprint
import copy

from pathlib import Path

class H5():
    pp = pprint.PrettyPrinter(indent=4)
    
    def transform(self, x):
        return x

    def inverse_transform(self, x):
        return x

    def __init__(self, *data):
        self.root = Dict()
        self.filename = None
        for i in data:
            self.root.update(copy.deepcopy(i))

    def load(self, paths=None, update=False):
        if self.filename is not None:
            with h5py.File(self.filename, 'r') as h5file:
                data = Dict(recursively_load(h5file, '/', self.inverse_transform, paths))
                if update:
                    self.root.update(data)
                else:
                    self.root = data
        else:
            print('Filename must be set before load can be used')

    def save(self):
        if self.filename is not None:
            with h5py.File(self.filename, 'w') as h5file:
                recursively_save(h5file, '/', self.root, self.transform)
        else:
            print("Filename must be set before save can be used")

    def append(self):
        "This can only be used to write new keys to the system, this is faster than having to read the data before writing it"
        if self.filename is not None:
            with h5py.File(self.filename, 'a') as h5file:
                recursively_save(h5file, '/', self.root, self.transform)
        else:
            print("Filename must be set before save can be used")

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

class Cadet(H5):
    #cadet_path must be set in order for simulations to run
    cadet_path = None
    return_information = None
    
    def transform(self, x):
        return str.upper(x)

    def inverse_transform(self, x):
        return str.lower(x)
    
    def run(self, timeout = None, check=None):
        if self.filename is not None:
            data = subprocess.run([self.cadet_path, self.filename], timeout = timeout, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.return_information = data
            return data
        else:
            print("Filename must be set before run can be used")

def recursively_load( h5file, path, func, paths): 

    ans = {}
    for key_original in h5file[path].keys():
        key = func(key_original)
        local_path = path + key
        if paths is None or (paths is not None and local_path in paths):
            item = h5file[path][key_original]
            if isinstance(item, h5py._hl.dataset.Dataset):
                ans[key] = item[()]
            elif isinstance(item, h5py._hl.group.Group):
                ans[key] = recursively_load(h5file, local_path + '/', func, paths)
    return ans 

def recursively_save( h5file, path, dic, func):

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
            h5file[path + func(key)] = numpy.array(item, dtype='S')
        
        elif isinstance(item, int):
            h5file[path + func(key)] = numpy.array(item, dtype=numpy.int32)
        
        elif isinstance(item, float):
            h5file[path + func(key)] = numpy.array(item, dtype=numpy.float64)
        
        elif isinstance(item, numpy.ndarray) and item.dtype == numpy.float64:
            h5file[path + func(key)] = item
        
        elif isinstance(item, numpy.ndarray) and item.dtype == numpy.float32:
            h5file[path + func(key)] = numpy.array(item, dtype=numpy.float64)
        
        elif isinstance(item, numpy.ndarray) and item.dtype == numpy.int32:
            h5file[path + func(key)] = item
        
        elif isinstance(item, numpy.ndarray) and item.dtype == numpy.int64:
            h5file[path + func(key)] = item.astype(numpy.int32)

        elif isinstance(item, numpy.ndarray) and item.dtype.kind == 'S':
            h5file[path + func(key)] = item
        
        elif isinstance(item, list) and all(isinstance(i, int) for i in item):
            h5file[path + func(key)] = numpy.array(item, dtype=numpy.int32)
        
        elif isinstance(item, list) and any(isinstance(i, float) for i in item):
            h5file[path + func(key)] = numpy.array(item, dtype=numpy.float64)
        
        elif isinstance(item, numpy.int32):
            h5file[path + func(key)] = item
        
        elif isinstance(item, numpy.float64):
            h5file[path + func(key)] = item

        elif isinstance(item, numpy.float32):
            h5file[path + func(key)] = numpy.array(item, dtype=numpy.float64)
        
        elif isinstance(item, numpy.bytes_):
            h5file[path + func(key)] = item
        
        elif isinstance(item, bytes):
            h5file[path + func(key)] = item

        elif isinstance(item, list) and all(isinstance(i, str) for i in item):
            h5file[path + func(key)] = numpy.array(item, dtype="S")

        # save dictionaries
        elif isinstance(item, dict):
            recursively_save(h5file, path + key + '/', item, func)
        # other types cannot be saved and will result in an error
        else:
            raise ValueError('Cannot save %s/%s key with %s type.' % (path, func(key), type(item)))
