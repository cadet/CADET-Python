
import ctypes
import numpy
import addict
import time

#input("Press Enter to continue...")

def log_handler(file, func, line, level, level_name, message):
    log_print('{} ({}:{:d}) {}'.format(level_name.decode('utf-8') , func.decode('utf-8') , line, message.decode('utf-8') ))

c_cadet_result = ctypes.c_int

def null(*args):
    pass

if 0:
    log_print = print
else:
    log_print = null


class PARAMETERPROVIDER(ctypes.Structure):

    _fields_ = [
        ('userData', ctypes.py_object),

        ('getDouble', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double))),
        ('getInt', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int))),
        ('getBool', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint8))),
        ('getString', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p))),

        ('getDoubleArray', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)))),
        ('getIntArray', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.POINTER(ctypes.c_int)))),
        ('getBoolArray', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8)))),
        ('getStringArray', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p)))),

        ('getDoubleArrayItem', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_double))),
        ('getIntArrayItem', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int))),
        ('getBoolArrayItem', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8))),
        ('getStringArrayItem', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p))),

        ('exists', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.py_object, ctypes.c_char_p)),
        ('isArray', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint8))),
        ('numElements', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.py_object, ctypes.c_char_p)),
        ('pushScope', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p)),
        ('popScope', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object)),
    ]


class CADETAPIV010000(ctypes.Structure):

    _fields_ = [
        ('createDriver', ctypes.CFUNCTYPE(ctypes.c_void_p)),
        ('deleteDriver', ctypes.CFUNCTYPE(None, ctypes.c_void_p)),
        ('runSimulation', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_void_p, ctypes.POINTER(PARAMETERPROVIDER))),
        ('getNParTypes', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int))),
        ('getSolutionInlet', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionOutlet', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionBulk', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionParticle', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionSolid', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionFlux', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionVolume', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionDerivativeInlet', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionDerivativeOutlet', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionDerivativeBulk', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionDerivativeParticle', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionDerivativeSolid', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionDerivativeFlux', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSolutionDerivativeVolume', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityInlet', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityOutlet', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityBulk', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityParticle', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivitySolid', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityFlux', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityVolume', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityDerivativeInlet', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityDerivativeOutlet', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityDerivativeBulk', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityDerivativeParticle', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityDerivativeSolid', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityDerivativeFlux', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityDerivativeVolume', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int) )),
        ('getSensitivityDerivativeVolume', ctypes.CFUNCTYPE(c_cadet_result, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.POINTER(ctypes.c_double)), ctypes.POINTER(ctypes.c_int) )),
    ]


class NestedDictReader:

    def __init__(self, data):
        self.__root = data
        self.__cursor = []
        self.__cursor.append(data)
        self.buffer = None

    def push_scope(self, scope):
        if scope in self.__cursor[-1]:
            log_print('Entering scope {}'.format(scope))
            self.__cursor.append(self.__cursor[-1][scope])
            return True

        return False

    def pop_scope(self):
        self.__cursor.pop()
        log_print('Exiting scope')

    def current(self):
        return self.__cursor[-1]


def param_provider_get_double(reader, name, val):
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]
        try:
            float_val = float(o)
        except TypeError:
            float_val = float(o[0])

        val[0] = ctypes.c_double(float_val)

        log_print('GET scalar [double] {}: {}'.format(n, float(val[0])))
        return 0

    return -1


def param_provider_get_int(reader, name, val):
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]
        try:
            int_val = int(o)
        except TypeError:
            int_val = int(o[0])

        val[0] = ctypes.c_int(int_val)

        log_print('GET scalar [int] {}: {}'.format(n, int(val[0])))
        return 0

    return -1


def param_provider_get_bool(reader, name, val):
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]

        try:
            int_val = int(o)
        except TypeError:
            int_val = int(o[0])

        val[0] = ctypes.c_uint8(int_val)

        log_print('GET scalar [bool] {}: {}'.format(n, bool(val[0])))
        return 0

    return -1


def param_provider_get_string(reader, name, val):
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]

        #we have one of array of strings, array of bytestrings, bytestring or string or something convertable to one of these
        if hasattr(o, 'encode'):
            bytes_val = o.encode('utf-8')
        elif hasattr(o, 'decode'):
            bytes_val = o
        elif hasattr(o[0], 'encode'):
            bytes_val = o[0].encode('utf-8')
        elif hasattr(o[0], 'decode'):
            bytes_val = o[0]

        reader.buffer = bytes_val
        val[0] = ctypes.cast(reader.buffer, ctypes.c_char_p)

        return 0

    return -1


def param_provider_get_double_array(reader, name, n_elem, val):
    n = name.decode('utf-8')
    c = reader.current()

    if (n in c):
        o = c[n]
        if isinstance(o, list):
            o = numpy.ascontiguousarray(o)
        if (not isinstance(o, numpy.ndarray)) or (o.dtype != numpy.double) or (not o.flags.c_contiguous):
            return -1

        n_elem[0] = ctypes.c_int(o.size)
        val[0] = o.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        log_print('GET array [double] {}: {}'.format(n, o))
        return 0

    return -1


def param_provider_get_int_array(reader, name, n_elem, val):
    n = name.decode('utf-8')
    c = reader.current()

    if (n in c):
        o = c[n]
        if isinstance(o, list):
            o = numpy.ascontiguousarray(o)
        if (not isinstance(o, numpy.ndarray)) or (o.dtype != numpy.int) or (not o.flags.c_contiguous):
            return -1

        n_elem[0] = ctypes.c_int(o.size)
        val[0] = o.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        log_print('GET array [int] {}: {}'.format(n, o))
        return 0

    return -1


def param_provider_get_double_array_item(reader, name, index, val):
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]

        try:
            float_val = float(o)
        except TypeError:
            float_val = float(o[index])

        val[0] = ctypes.c_double(float_val)
        log_print('GET array [double] ({}) {}: {}'.format(index, n, val[0]))
        return 0

    return -1


def param_provider_get_int_array_item(reader, name, index, val):
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]

        try:
            int_val = int(o)
        except TypeError:
            int_val = int(o[index])

        val[0] = ctypes.c_int(int_val)
        log_print('GET array [int] ({}) {}: {}'.format(index, n, val[0]))
        return 0

    return -1


def param_provider_get_bool_array_item(reader, name, index, val):
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]

        try:
            int_val = int(o)
        except TypeError:
            int_val = int(o[index])

        val[0] = ctypes.c_uint8(int_val)
        log_print('GET array [bool] ({}) {}: {}'.format(index, n, bool(val[0])))
        return 0

    return -1


def param_provider_get_string_array_item(reader, name, index, val):
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]
        if index == 0:
            if hasattr(o, 'encode'):
                bytes_val = o.encode('utf-8')
            elif hasattr(o, 'decode'):
                bytes_val = o
        else:
            if hasattr(o[index], 'encode'):
                bytes_val = o[index].encode('utf-8')
            elif hasattr(o[index], 'decode'):
                bytes_val = o[index]

        reader.buffer = bytes_val
        val[0] = ctypes.cast(reader.buffer, ctypes.c_char_p)
        log_print('GET array [string] ({}) {}: {}'.format(index, n, reader.buffer.decode('utf-8')))
        return 0

    return -1


def param_provider_exists(reader, name):
    n = name.decode('utf-8')
    c = reader.current()

    log_print('EXISTS {}: {}'.format(n, n in c))

    if n in c:
        return 1

    return 0


def param_provider_is_array(reader, name, res):
    n = name.decode('utf-8')
    c = reader.current()

    if n not in c:
        return -1

    o = c[n]
    res[0] = ctypes.c_uint8(0)
    if isinstance(o, list):
        res[0] = ctypes.c_uint8(1)
    elif isinstance(o, numpy.ndarray):
        res[0] = ctypes.c_uint8(1)

    log_print('ISARRAY {}: {}'.format(n, bool(res[0])))

    return 0


def param_provider_num_elements(reader, name):
    n = name.decode('utf-8')
    c = reader.current()

    if n not in c:
        return -1

    o = c[n]
    if isinstance(o, list):
        log_print('NUMELEMENTS {}: {}'.format(n, len(o)))
        return len(o)
    elif isinstance(o, numpy.ndarray):
        log_print('NUMELEMENTS {}: {}'.format(n, o.size))
        return o.size

    log_print('NUMELEMENTS {}: {}'.format(n, 1))
    return 1


def param_provider_push_scope(reader, name):
    n = name.decode('utf-8')

    if reader.push_scope(n):
        return 0
    else:
        return -1


def param_provider_pop_scope(reader):
    reader.pop_scope()
    return 0


class SimulationResult:

    def __init__(self, api, driver):
        self.__api = api
        self.__driver = driver

    def inlet(self, unit, own_data=True):
        c_double_p = ctypes.POINTER(ctypes.c_double)
        time_ptr = c_double_p()
        data_ptr = c_double_p()
        n_time = ctypes.c_int()
        n_ports = ctypes.c_int()
        n_comp = ctypes.c_int()

        result = self.__api.getSolutionInlet(self.__driver, unit, ctypes.byref(time_ptr), ctypes.byref(data_ptr), ctypes.byref(n_time), ctypes.byref(n_ports), ctypes.byref(n_comp))
        n_time = n_time.value
        n_ports = n_ports.value
        n_comp = n_comp.value

        data = numpy.ctypeslib.as_array(data_ptr, shape=(n_time, n_ports, n_comp))
        time = numpy.ctypeslib.as_array(time_ptr, shape=(n_time, ))

        if own_data:
            return (time.copy(), data.copy())
        else:
            return (time, data)

    def outlet(self, unit, own_data=True):
        c_double_p = ctypes.POINTER(ctypes.c_double)
        time_ptr = c_double_p()
        data_ptr = c_double_p()
        n_time = ctypes.c_int()
        n_ports = ctypes.c_int()
        n_comp = ctypes.c_int()

        result = self.__api.getSolutionOutlet(
            self.__driver,
            unit,
            ctypes.byref(time_ptr),
            ctypes.byref(data_ptr),
            ctypes.byref(n_time),
            ctypes.byref(n_ports),
            ctypes.byref(n_comp)
        )
        n_time = n_time.value
        n_ports = n_ports.value
        n_comp = n_comp.value

        data = numpy.ctypeslib.as_array(data_ptr, shape=(n_time, n_ports, n_comp))
        time = numpy.ctypeslib.as_array(time_ptr, shape=(n_time, ))

        if own_data:
            return (time.copy(), data.copy())
        else:
            return (time, data)

    def bulk(self, unit, own_data=True):
        c_double_p = ctypes.POINTER(ctypes.c_double)
        time_ptr = c_double_p()
        data_ptr = c_double_p()
        n_time = ctypes.c_int()
        n_axial_cells = ctypes.c_int()
        n_radial_cells = ctypes.c_int()
        n_comp = ctypes.c_int()

        result = self.__api.getSolutionBulk(
            self.__driver, unit,
            ctypes.byref(time_ptr),
            ctypes.byref(data_ptr),
            ctypes.byref(n_time),
            ctypes.byref(n_axial_cells),
            ctypes.byref(n_radial_cells),
            ctypes.byref(n_comp)
        )
        n_time = n_time.value
        n_axial_cells = n_axial_cells.value
        n_radial_cells = n_radial_cells.value
        n_comp = n_comp.value

        data = numpy.ctypeslib.as_array(data_ptr, shape=(n_time, n_axial_cells, n_radial_cells, n_comp))
        time = numpy.ctypeslib.as_array(time_ptr, shape=(n_time, ))

        if own_data:
            return (time.copy(), data.copy())
        else:
            return (time, data)

    def particle(self, unit, own_data=True):
        pass

    def solid(self, unit, own_data=True):
        pass

    def flux(self, unit, own_data=True):
        pass

    def volume(self, unit, own_data=True):
        pass

    def derivativeInlet(self, unit, own_data=True):
        pass

    def derivativeOutlet(self, unit, own_data=True):
        pass

    def derivativeBulk(self, unit, own_data=True):
        pass

    def derivativeParticle(self, unit, own_data=True):
        pass

    def derivativeSolid(self, unit, own_data=True):
        pass

    def derivativeFlux(self, unit, own_data=True):
        pass

    def derivativeVolume(self, unit, own_data=True):
        pass

    def sensitivityInlet(self, unit, own_data=True):
        pass

    def sensitivityOutlet(self, unit, own_data=True):
        pass

    def sensitivityBulk(self, unit, own_data=True):
        pass

    def sensitivityParticle(self, unit, own_data=True):
        pass

    def sensitivitySolid(self, unit, own_data=True):
        pass

    def sensitivityFlux(self, unit, own_data=True):
        pass

    def sensitivityVolume(self, unit, own_data=True):
        pass

    def sensitivityDerivativeInlet(self, unit, own_data=True):
        pass

    def sensitivityDerivativeOutlet(self, unit, own_data=True):
        pass

    def sensitivityDerivativeBulk(self, unit, own_data=True):
        pass

    def sensitivityDerivativeParticle(self, unit, own_data=True):
        pass

    def sensitivityDerivativeSolid(self, unit, own_data=True):
        pass

    def sensitivityDerivativeFlux(self, unit, own_data=True):
        pass

    def sensitivityDerivativeVolume(self, unit, own_data=True):
        pass

class CadetDLL:

    def __init__(self, dll_path):
        self.cadet_path = dll_path
        self.__lib = ctypes.cdll.LoadLibrary(dll_path)

        # Query meta information
        cdtGetLibraryVersion = self.__lib.cdtGetLibraryVersion
        cdtGetLibraryVersion.restype = ctypes.c_char_p
        self.cadet_version = cdtGetLibraryVersion().decode('utf-8')

        cdtGetLibraryCommitHash = self.__lib.cdtGetLibraryCommitHash
        cdtGetLibraryCommitHash.restype = ctypes.c_char_p
        self.cadet_commit_hash = cdtGetLibraryCommitHash().decode('utf-8')

        cdtGetLibraryBranchRefspec = self.__lib.cdtGetLibraryBranchRefspec
        cdtGetLibraryBranchRefspec.restype = ctypes.c_char_p
        self.cadet_branch = cdtGetLibraryBranchRefspec().decode('utf-8')

        cdtGetLibraryBuildType = self.__lib.cdtGetLibraryBuildType
        cdtGetLibraryBuildType.restype = ctypes.c_char_p
        self.cadet_build_type = cdtGetLibraryBuildType().decode('utf-8')

        # Enable logging
        LOG_HANDLER_CLBK = ctypes.CFUNCTYPE(
            None,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_uint,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_char_p
        )
        set_log_handler = self.__lib.cdtSetLogReceiver
        set_log_handler.argtypes = [LOG_HANDLER_CLBK]
        set_log_handler.restype = None
        # Keep reference alive by assigning it to this Python object
        self.__log_handler = LOG_HANDLER_CLBK(log_handler)
        set_log_handler(self.__log_handler)

        self.__set_log_level = self.__lib.cdtSetLogLevel
        self.__set_log_level.argtypes = [ctypes.c_int]
        self.__set_log_level.restype = None
        self.__set_log_level(2)

        # Query API
        cdtGetAPIv010000 = self.__lib.cdtGetAPIv010000
        cdtGetAPIv010000.argtypes = [ctypes.POINTER(CADETAPIV010000)]
        cdtGetAPIv010000.restype = c_cadet_result

        self.__api = CADETAPIV010000()
        cdtGetAPIv010000(ctypes.byref(self.__api))

        self.__driver = self.__api.createDriver()

    def clear(self):
        if hasattr(self, "res"):
            del self.res
        self.__api.deleteDriver(self.__driver)
        self.__driver = self.__api.createDriver()

    def __del__(self):
        log_print('deleteDriver()')
        self.__api.deleteDriver(self.__driver)


    def run(self, filename = None, simulation=None, timeout = None, check=None):
        pp = PARAMETERPROVIDER()

        sim_input = recursively_convert_dict(simulation)

        pp.userData = NestedDictReader(sim_input)

        pp.getDouble = PARAMETERPROVIDER._fields_[1][1](param_provider_get_double)
        pp.getInt = PARAMETERPROVIDER._fields_[2][1](param_provider_get_int)
        pp.getBool = PARAMETERPROVIDER._fields_[3][1](param_provider_get_bool)
        pp.getString = PARAMETERPROVIDER._fields_[4][1](param_provider_get_string)

        pp.getDoubleArray = PARAMETERPROVIDER._fields_[5][1](param_provider_get_double_array)
        pp.getIntArray = PARAMETERPROVIDER._fields_[6][1](param_provider_get_int_array)
        pp.getBoolArray = ctypes.cast(None, PARAMETERPROVIDER._fields_[7][1])
        pp.getStringArray = ctypes.cast(None, PARAMETERPROVIDER._fields_[8][1])

        pp.getDoubleArrayItem = PARAMETERPROVIDER._fields_[9][1](param_provider_get_double_array_item)
        pp.getIntArrayItem = PARAMETERPROVIDER._fields_[10][1](param_provider_get_int_array_item)
        pp.getBoolArrayItem = PARAMETERPROVIDER._fields_[11][1](param_provider_get_bool_array_item)
        pp.getStringArrayItem = PARAMETERPROVIDER._fields_[12][1](param_provider_get_string_array_item)

        pp.exists = PARAMETERPROVIDER._fields_[13][1](param_provider_exists)
        pp.isArray = PARAMETERPROVIDER._fields_[14][1](param_provider_is_array)
        pp.numElements = PARAMETERPROVIDER._fields_[15][1](param_provider_num_elements)
        pp.pushScope = PARAMETERPROVIDER._fields_[16][1](param_provider_push_scope)
        pp.popScope = PARAMETERPROVIDER._fields_[17][1](param_provider_pop_scope)

        self.__api.runSimulation(self.__driver, ctypes.byref(pp))
        self.res = SimulationResult(self.__api, self.__driver)
        return self.res

    def load_inlet(self, sim):
        inlet = addict.Dict()
        if self.res is not None:
            for key,value in sim.root.input['return'].items():
                if key.startswith('unit'):
                    if value.write_solution_inlet:
                        unit = int(key[-3:])
                        t, out = self.res.inlet(unit)

                        if not len(inlet.solution_times):
                            inlet.solution_times = t

                        for comp in range(out.shape[2]):
                            comp_out = numpy.squeeze(out[:,:,comp])
                            inlet[key]['solution_inlet_comp_%03d' % comp] = comp_out
        return inlet

    def load_outlet(self, sim):
        outlet = addict.Dict()
        if self.res is not None:
            for key,value in sim.root.input['return'].items():
                if key.startswith('unit'):
                    if value.write_solution_outlet:
                        unit = int(key[-3:])
                        t, out = self.res.outlet(unit)

                        if not len(outlet.solution_times):
                            outlet.solution_times = t

                        for comp in range(out.shape[2]):
                            comp_out = numpy.squeeze(out[:,:,comp])
                            outlet[key]['solution_outlet_comp_%03d' % comp] = comp_out
        return outlet

    def load_bulk(self, sim):
        bulk = addict.Dict()
        if self.res is not None:
            for key,value in sim.root.input['return'].items():
                if key.startswith('unit'):
                    if value.write_solution_bulk:
                        unit = int(key[-3:])
                        t, out = self.res.bulk(unit)

                        if not len(bulk.solution_times):
                            bulk.solution_times = t

                        bulk[key]['solution_bulk'] = out
        return bulk

    def load_particle(sim):
        pass

    def load_solid(sim):
        pass

    def load_flux(sim):
        pass

    def load_volume(sim):
        pass

    def load_derivative_inlet(sim):
        pass

    def load_derivative_outlet(sim):
        pass

    def load_derivative_bulk(sim):
        pass

    def load_derivative_particle(sim):
        pass

    def load_derivative_solid(sim):
        pass

    def load_derivative_flux(sim):
        pass

    def load_derivative_volume(sim):
        pass

    def load_sensitivity_inlet(sim):
        pass

    def load_sensitivity_outlet(sim):
        pass

    def load_sensitivity_bulk(sim):
        pass

    def load_sensitivity_particle(sim):
        pass

    def load_sensitivity_solid(sim):
        pass

    def load_sensitivity_flux(sim):
        pass

    def load_sensitivity_volume(sim):
        pass

    def load_sensitivity_derivative_inlet(sim):
        pass

    def load_sensitivity_derivative_outlet(sim):
        pass

    def load_sensitivity_derivative_bulk(sim):
        pass

    def load_sensitivity_derivative_particle(sim):
        pass

    def load_sensitivity_derivative_solid(sim):
        pass

    def load_sensitivity_derivative_flux(sim):
        pass

    def load_sensitivity_derivative_volume(sim):
        pass

    def load_results(self, sim):
        sim.root.output.solution.update(self.load_inlet(sim))
        sim.root.output.solution.update(self.load_outlet(sim))
        sim.root.output.solution.update(self.load_bulk(sim))
        sim.root.output.solution.update(self.load_particle(sim))
        sim.root.output.solution.update(self.load_solid(sim))
        sim.root.output.solution.update(self.load_flux(sim))
        sim.root.output.solution.update(self.load_volume(sim))
        sim.root.output.solution.update(self.load_derivative_inlet(sim))
        sim.root.output.solution.update(self.load_derivative_outlet(sim))
        sim.root.output.solution.update(self.load_derivative_bulk(sim))
        sim.root.output.solution.update(self.load_derivative_particle(sim))
        sim.root.output.solution.update(self.load_derivative_solid(sim))
        sim.root.output.solution.update(self.load_derivative_flux(sim))
        sim.root.output.solution.update(self.load_derivative_volume(sim))
        sim.root.output.solution.update(self.load_sensitivity_inlet(sim))
        sim.root.output.solution.update(self.load_sensitivity_outlet(sim))
        sim.root.output.solution.update(self.load_sensitivity_bulk(sim))
        sim.root.output.solution.update(self.load_sensitivity_particle(sim))
        sim.root.output.solution.update(self.load_sensitivity_solid(sim))
        sim.root.output.solution.update(self.load_sensitivity_flux(sim))
        sim.root.output.solution.update(self.load_sensitivity_volume(sim))
        sim.root.output.solution.update(self.load_sensitivity_derivative_inlet(sim))
        sim.root.output.solution.update(self.load_sensitivity_derivative_outlet(sim))
        sim.root.output.solution.update(self.load_sensitivity_derivative_bulk(sim))
        sim.root.output.solution.update(self.load_sensitivity_derivative_particle(sim))
        sim.root.output.solution.update(self.load_sensitivity_derivative_solid(sim))
        sim.root.output.solution.update(self.load_sensitivity_derivative_flux(sim))
        sim.root.output.solution.update(self.load_sensitivity_derivative_volume(sim))


def recursively_convert_dict(data):
    ans = addict.Dict()
    for key_original, item in data.items():
        if isinstance(item, dict):
            ans[key_original] = recursively_convert_dict(item)
        else:
            key = str.upper(key_original)
            ans[key] = item
    return ans
