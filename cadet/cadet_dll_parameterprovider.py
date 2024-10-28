import ctypes
import cadet.cadet_dll_utils as utils
import addict
from typing import Any, Dict, Optional, Union


c_cadet_result = ctypes.c_int
array_double = ctypes.POINTER(ctypes.POINTER(ctypes.c_double))
point_int = ctypes.POINTER(ctypes.c_int)


def null(*args: Any) -> None:
    pass


if 0:
    log_print = print
else:
    log_print = null


class NestedDictReader:
    """
    Utility class to read and navigate through nested dictionaries.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        self._root = data
        self._cursor = [data]
        self.buffer: Optional[Any] = None

    def push_scope(self, scope: str) -> bool:
        """
        Enter a nested scope within the dictionary.

        Parameters
        ----------
        scope : str
            The key representing the nested scope.

        Returns
        -------
        bool
            True if the scope exists and was entered, otherwise False.
        """
        if scope in self._cursor[-1]:
            log_print(f'Entering scope {scope}')
            self._cursor.append(self._cursor[-1][scope])
            return True
        return False

    def pop_scope(self) -> None:
        """
        Exit the current scope.
        """
        if len(self._cursor) > 1:
            self._cursor.pop()
            log_print('Exiting scope')

    def current(self) -> Any:
        """
        Get the current scope data.

        Returns
        -------
        Any
            The current data under the scope.
        """
        return self._cursor[-1]


def recursively_convert_dict(data: Dict[str, Any]) -> addict.Dict:
    """
    Recursively convert dictionary keys to uppercase while preserving nested structure.

    Parameters
    ----------
    data : dict
        The dictionary to convert.

    Returns
    -------
    addict.Dict
        A new dictionary with all keys converted to uppercase.
    """
    ans = addict.Dict()
    for key_original, item in data.items():
        if isinstance(item, dict):
            ans[key_original] = recursively_convert_dict(item)
        else:
            key = str.upper(key_original)
            ans[key] = item
    return ans


class PARAMETERPROVIDER(ctypes.Structure):
    """
    Implement the CADET Parameter Provider interface, allowing querying Python for parameters.

    This class exposes various function pointers as fields in a ctypes structure
    to be used with CADET's C-API.

    Parameters
    ----------
    simulation : Cadet
        The simulation object containing the input data.
    """

    def __init__(self, simulation: "Cadet") -> None:
        sim_input = recursively_convert_dict(simulation.root.input)
        self.userData = NestedDictReader(sim_input)

        # Assign function pointers at instance level
        self.getDouble = self._fields_[1][1](utils.param_provider_get_double)
        self.getInt = self._fields_[2][1](utils.param_provider_get_int)
        self.getBool = self._fields_[3][1](utils.param_provider_get_bool)
        self.getString = self._fields_[4][1](utils.param_provider_get_string)

        self.getDoubleArray = self._fields_[5][1](utils.param_provider_get_double_array)
        self.getIntArray = self._fields_[6][1](utils.param_provider_get_int_array)
        self.getBoolArray = ctypes.cast(None, self._fields_[7][1])
        self.getStringArray = ctypes.cast(None, self._fields_[8][1])

        self.getDoubleArrayItem = self._fields_[9][1](utils.param_provider_get_double_array_item)
        self.getIntArrayItem = self._fields_[10][1](utils.param_provider_get_int_array_item)
        self.getBoolArrayItem = self._fields_[11][1](utils.param_provider_get_bool_array_item)
        self.getStringArrayItem = self._fields_[12][1](utils.param_provider_get_string_array_item)

        self.exists = self._fields_[13][1](utils.param_provider_exists)
        self.isArray = self._fields_[14][1](utils.param_provider_is_array)
        self.numElements = self._fields_[15][1](utils.param_provider_num_elements)
        self.pushScope = self._fields_[16][1](utils.param_provider_push_scope)
        self.popScope = self._fields_[17][1](utils.param_provider_pop_scope)

    _fields_ = [
        ('userData', ctypes.py_object),

        ('getDouble', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double))),
        ('getInt', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, point_int)),
        ('getBool', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint8))),
        ('getString', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p))),

        ('getDoubleArray', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, point_int, array_double)),
        ('getIntArray', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, point_int, ctypes.POINTER(point_int))),
        ('getBoolArray', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, point_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8)))),
        ('getStringArray', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, point_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p)))),

        ('getDoubleArrayItem', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_double))),
        ('getIntArrayItem', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.c_int, point_int)),
        ('getBoolArrayItem', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8))),
        ('getStringArrayItem', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p))),

        ('exists', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.py_object, ctypes.c_char_p)),
        ('isArray', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint8))),
        ('numElements', ctypes.CFUNCTYPE(ctypes.c_int, ctypes.py_object, ctypes.c_char_p)),
        ('pushScope', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object, ctypes.c_char_p)),
        ('popScope', ctypes.CFUNCTYPE(c_cadet_result, ctypes.py_object)),
    ]
