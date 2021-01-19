from addict import Dict

import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=FutureWarning)
    import h5py
import numpy
import subprocess
import pprint
import copy
import json

import filelock
import contextlib

from pathlib import Path

from cadet.cadet_dll import CadetDLL

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

    def load(self, paths=None, update=False, lock=False):
        if self.filename is not None:

            if lock is True:
                lock_file = filelock.FileLock(self.filename + '.lock')
            else:
                lock_file = contextlib.nullcontext()

            with lock_file:
                with h5py.File(self.filename, 'r') as h5file:
                    data = Dict(recursively_load(h5file, '/', self.inverse_transform, paths))
                    if update:
                        self.root.update(data)
                    else:
                        self.root = data
        else:
            print('Filename must be set before load can be used')

    def save(self, lock=False):
        if self.filename is not None:
            if lock is True:
                lock_file = filelock.FileLock(self.filename + '.lock')
            else:
                lock_file = contextlib.nullcontext()

            with lock_file:
                with h5py.File(self.filename, 'w') as h5file:
                    recursively_save(h5file, '/', self.root, self.transform)
        else:
            print("Filename must be set before save can be used")

    def save_json(self, filename):
        with Path(filename).open("w") as fp:
            data = convert_from_numpy(self.root, self.transform)
            json.dump(data, fp, indent=4, sort_keys=True)

    def load_json(self, filename, update=False):
        with Path(filename).open("r") as fp:
            data = json.load(fp)
            data = recursively_load_dict(data, self.inverse_transform)
            if update:
                self.root.update(data)
            else:
                self.root = data

    def append(self, lock=False):
        "This can only be used to write new keys to the system, this is faster than having to read the data before writing it"
        if self.filename is not None:
            if lock is True:
                lock_file = filelock.FileLock(self.filename + '.lock')
            else:
                lock_file = contextlib.nullcontext()

            with lock_file:
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

def is_dll(value):
    suffix = Path(value).suffix
    return suffix in {'.so', '.dll'}

class Cadet(H5):
    #cadet_path must be set in order for simulations to run
    cadet_runner = None
    return_information = None

    @property
    def cadet_path(self):
        if self.cadet_runner is not None:
            return self.cadet_runner.cadet_path

    @cadet_path.setter
    def cadet_path(self, value):
        if self.cadet_runner is not None and self.cadet_runner.cadet_path != value:
            del self.cadet_runner

        if is_dll(value):
            self.cadet_runner  = CadetDLL(value)
        else:
            self.cadet_runner = CadetFile(value)

    @cadet_path.deleter
    def cadet_path(self):
        del self.cadet_runner

    
    def transform(self, x):
        return str.upper(x)

    def inverse_transform(self, x):
        return str.lower(x)
    
    def run(self, timeout = None, check=None):
        data = self.cadet_runner.run(simulation=self.root, filename=self.filename, timeout=timeout, check=check)
        #self.return_information = data
        return data
        

class CadetFile:

    def __init__(self, cadet_path):
        self.cadet_path = cadet_path

    def run(self, filename = None, simulation=None, timeout = None, check=None):
        if filename is not None:
            data = subprocess.run([self.cadet_path, filename], timeout = timeout, check=check, capture_output=True)
            return data
        else:
            print("Filename must be set before run can be used")

def convert_from_numpy(data, func):
    ans = Dict()
    for key_original,item in data.items():
        key = func(key_original)
        if isinstance(item, numpy.ndarray):
            item = item.tolist()
        
        if isinstance(item, numpy.generic):
            item = item.item()

        if isinstance(item, bytes):
            item = item.decode('ascii')
        
        if isinstance(item, Dict):
            ans[key_original] = convert_from_numpy(item, func)
        else:
            ans[key] = item
    return ans

def recursively_load_dict( data, func): 
    ans = Dict()
    for key_original,item in data.items():
        key = func(key_original)
        if isinstance(item, dict):
            ans[key] = recursively_load_dict(item, func)
        else:
            ans[key] = item
    return ans

def set_path(obj, path, value):
    "paths need to be broken up so that subobjects are correctly made"
    path = path.split('/')
    path = [i for i in path if i]

    temp = obj
    for part in path[:-1]:
        temp = temp[part]

    temp[path[-1]] = value

def recursively_load( h5file, path, func, paths): 
    ans = Dict()
    if paths is not None:
        for path in paths:
            item = h5file.get(path, None)
            if item is not None:
                if isinstance(item, h5py._hl.dataset.Dataset):
                    set_path(ans, path, item[()])
                elif isinstance(item, h5py._hl.group.Group):
                    set_path(ans, path, recursively_load(h5file, path + '/', func, None))
    else:
        for key_original in h5file[path].keys():
            key = func(key_original)
            local_path = path + key
            item = h5file[path][key_original]
            if isinstance(item, h5py._hl.dataset.Dataset):
                ans[key] = item[()]
            elif isinstance(item, h5py._hl.group.Group):
                ans[key] = recursively_load(h5file, local_path + '/', func, None)
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
            h5file[path + func(key)] = numpy.array(item.encode('ascii'))
        elif isinstance(item, list) and all(isinstance(i, str) for i in item):
            h5file[path + func(key)] = numpy.array([i.encode('ascii') for i in item])
        elif isinstance(item, dict):
            recursively_save(h5file, path + key + '/', item, func)
        else:
            try:
                h5file[path + func(key)] = numpy.array(item)
            except TypeError:
                raise ValueError('Cannot save %s/%s key with %s type.' % (path, func(key), type(item)))
