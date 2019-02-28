#Python 3.5+
#Depends on addict  https://github.com/mewwts/addict
#Depends on h5py, numpy

from addict import Dict

import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=FutureWarning)
    import h5py
import numpy
import subprocess
import pprint
import copy
import ctypes

class Cadet():

    #cadet_path must be set in order for simulations to run
    cadet_path = None
    cadet_library_path = None
    return_information = None

    pp = pprint.PrettyPrinter(indent=4)

    def __init__(self, *data):
        self.root = Dict()
        self.filename = None
        for i in data:
            self.root.update(copy.deepcopy(i))

    def load(self):
        if self.filename is not None:
            with h5py.File(self.filename, 'r') as h5file:
                self.root = Dict(recursively_load(h5file, '/'))
        else:
            print('Filename must be set before load can be used')

    load_file = load

    def load_memory(self):
       self.root = recursively_load_memory(self.memory)

    def save(self):
        if self.filename is not None:
            with h5py.File(self.filename, 'w') as h5file:
                recursively_save(h5file, '/', self.root)
        else:
            print("Filename must be set before save can be used")

    save_file = save

    def save_memory(self):
        self.memory, self.struct_class = recursively_save_memory(self.root)

    def run(self, timeout = None, check=None):
        if self.filename is not None:
            data = subprocess.run([self.cadet_path, self.filename], timeout = timeout, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.return_information = data
            return data
        else:
            print("Filename must be set before run can be used")

    run_file = run

    def run_memory(self):
        cadet_dll = ctypes.cdll.LoadLibrary(self.cadet_library_path)
        print(self.memory)

        cadet_dll.cadetGetLibraryVersion.restype = ctypes.c_char_p
        print(cadet_dll.cadetGetLibraryVersion().decode())

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
            h5file[path + key.upper()] = numpy.array(item, dtype='S')
        
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

        elif isinstance(item, numpy.ndarray) and item.dtype.kind == 'S':
            h5file[path + key.upper()] = item
        
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

        elif isinstance(item, list) and all(isinstance(i, str) for i in item):
            h5file[path + key.upper()] = numpy.array(item, dtype="S")

        # save dictionaries
        elif isinstance(item, dict):
            recursively_save(h5file, path + key + '/', item)
        # other types cannot be saved and will result in an error
        else:
            raise ValueError('Cannot save %s/%s key with %s type.' % (path, key.upper(), type(item)))


def recursively_save_memory(dic):

    # argument type checking
    if not isinstance(dic, dict):
        raise ValueError("must provide a dictionary")        

    class TempClass(ctypes.Structure):
        pass

    # save items to the hdf5 file
    _fields_ = []
    values = {}
    for key, item in dic.items():
        key = str(key)
        if not isinstance(key, str):
            raise ValueError("dict keys must be strings to save to hdf5")
        #handle   int, float, string and ndarray of int32, int64, float64
        if isinstance(item, str):
            _fields_.append( (key.upper(), ctypes.c_char_p) ) 
            
            values[key.upper()] = item
        
        elif isinstance(item, int):
            _fields_.append( (key.upper(), ctypes.c_int ) )

            values[key.upper()] = item
        
        elif isinstance(item, float):
            _fields_.append( (key.upper(), ctypes.c_double ) )

            values[key.upper()] = item
        
        elif isinstance(item, numpy.ndarray) and item.dtype == numpy.float64:
            _fields_.append( (key.upper(), ctypes.POINTER(ctypes.c_double) ) ) 

            values[key.upper()] = item.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
        elif isinstance(item, numpy.ndarray) and item.dtype == numpy.float32:
            _fields_.append( (key.upper(), ctypes.POINTER(ctypes.c_double) ) ) 

            values[key.upper()] = numpy.array(item, dtype=numpy.float64).ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
        elif isinstance(item, numpy.ndarray) and item.dtype == numpy.int32:
            _fields_.append( (key.upper(), ctypes.POINTER(ctypes.c_int) ) )
            
            values[key.upper()] = item.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        
        elif isinstance(item, numpy.ndarray) and item.dtype == numpy.int64:
            _fields_.append( (key.upper(), ctypes.POINTER(ctypes.c_int) ) ) 

            values[key.upper()] =item.astype(numpy.int32).ctypes.data_as(ctypes.POINTER(ctypes.c_int))

        elif isinstance(item, numpy.ndarray) and item.dtype.kind == 'S':
            _fields_.append( (key.upper(), ctypes.c_char_p) ) 

            values[key.upper()] = item.ctypes.data_as(ctypes.c_char_p)
        
        elif isinstance(item, list) and all(isinstance(i, int) for i in item):
            _fields_.append( (key.upper(), ctypes.POINTER(ctypes.c_int) ) ) 
            
            values[key.upper()] = numpy.array(item, dtype=numpy.int32).ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        
        elif isinstance(item, list) and any(isinstance(i, float) for i in item):
            _fields_.append( (key.upper(), ctypes.POINTER(ctypes.c_double) ) ) 

            values[key.upper()] = numpy.array(item, dtype=numpy.float64).ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
        elif isinstance(item, numpy.int32):
            _fields_.append( (key.upper(), ctypes.c_int ) ) 

            values[key.upper()] = int(item)
        
        elif isinstance(item, numpy.float64):
            _fields_.append( (key.upper(), ctypes.c_double ) )

            values[key.upper()] = float(item)

        elif isinstance(item, numpy.float32):
            _fields_.append( (key.upper(), ctypes.c_double ) ) 

            values[key.upper()] = float(item)
        
        elif isinstance(item, numpy.bytes_):
            _fields_.append( (key.upper(), ctypes.c_char_p) ) 

            values[key.upper()] = item
        
        elif isinstance(item, bytes):
            _fields_.append( (key.upper(), ctypes.c_char_p) ) 

            values[key.upper()] = item

        elif isinstance(item, list) and all(isinstance(i, str) for i in item):
            _fields_.append( (key.upper(), ctypes.POINTER(ctypes.c_char_p)) )

            values[key.upper()] = numpy.array(item, dtype="S").ctypes.data_as(ctypes.POINTER(ctypes.c_char_p))

        # save dictionaries
        elif isinstance(item, dict):
            temp_recur, TempClass_recur = recursively_save_memory(item)
            _fields_.append( (key, TempClass_recur ) )
            values[key] = temp_recur
        # other types cannot be saved and will result in an error
        else:
            raise ValueError('Cannot save %s/%s key with %s type.' % (path, key.upper(), type(item)))

    TempClass._fields_ = _fields_
    temp = TempClass(**values)
    #a = None
    return temp, TempClass
