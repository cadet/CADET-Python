import ctypes
import numpy as np
from typing import Any, Optional


def null(*args: Any) -> None:
    """Do nothing (used as a placeholder function)."""
    pass

log_print = print if 0 else null

def param_provider_get_double(
        reader: Any,
        name: ctypes.c_char_p,
        val: ctypes.POINTER(ctypes.c_double)
        ) -> int:
    """
    Retrieve a double value from the reader based on the provided name.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to retrieve.
    val : ctypes.POINTER(ctypes.c_double)
        A pointer to store the retrieved double value.

    Returns
    -------
    int
        0 if the value was found and retrieved successfully, -1 otherwise.
    """
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]
        try:
            float_val = float(o)
        except TypeError:
            float_val = float(o[0])

        val[0] = ctypes.c_double(float_val)
        log_print(f"GET scalar [double] {n}: {float(val[0])}")
        return 0

    return -1


def param_provider_get_int(
        reader: Any,
        name: ctypes.c_char_p,
        val: ctypes.POINTER(ctypes.c_int)
        ) -> int:
    """
    Retrieve an integer value from the reader based on the provided name.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to retrieve.
    val : ctypes.POINTER(ctypes.c_int)
        A pointer to store the retrieved integer value.

    Returns
    -------
    int
        0 if the value was found and retrieved successfully, -1 otherwise.
    """
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]
        try:
            int_val = int(o)
        except TypeError:
            int_val = int(o[0])

        val[0] = ctypes.c_int(int_val)
        log_print(f"GET scalar [int] {n}: {int(val[0])}")
        return 0

    return -1


def param_provider_get_bool(
        reader: Any,
        name: ctypes.c_char_p,
        val: ctypes.POINTER(ctypes.c_uint8)
        ) -> int:
    """
    Retrieve a boolean value from the reader based on the provided name.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to retrieve.
    val : ctypes.POINTER(ctypes.c_uint8)
        A pointer to store the retrieved boolean value.

    Returns
    -------
    int
        0 if the value was found and retrieved successfully, -1 otherwise.
    """
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]
        try:
            int_val = int(o)
        except TypeError:
            int_val = int(o[0])

        val[0] = ctypes.c_uint8(int_val)
        log_print(f"GET scalar [bool] {n}: {bool(val[0])}")
        return 0

    return -1


def param_provider_get_string(
        reader: Any,
        name: ctypes.c_char_p,
        val: ctypes.POINTER(ctypes.c_char_p)
        ) -> int:
    """
    Retrieve a string value from the reader based on the provided name.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to retrieve.
    val : ctypes.POINTER(ctypes.c_char_p)
        A pointer to store the retrieved string value.

    Returns
    -------
    int
        0 if the value was found and retrieved successfully, -1 otherwise.
    """
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]

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


def param_provider_get_double_array(
        reader: Any,
        name: ctypes.c_char_p,
        n_elem: ctypes.POINTER(ctypes.c_int),
        val: ctypes.POINTER(ctypes.POINTER(ctypes.c_double))
        ) -> int:
    """
    Retrieve a double array from the reader based on the provided name.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to retrieve.
    n_elem : ctypes.POINTER(ctypes.c_int)
        A pointer to store the number of elements in the array.
    val : ctypes.POINTER(ctypes.POINTER(ctypes.c_double))
        A pointer to store the retrieved array.

    Returns
    -------
    int
        0 if the array was found and retrieved successfully, -1 otherwise.
    """
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]
        if isinstance(o, list):
            o = np.ascontiguousarray(o)
        if not isinstance(o, np.ndarray) or o.dtype != np.double or not o.flags.c_contiguous:
            return -1

        n_elem[0] = ctypes.c_int(o.size)
        val[0] = o.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        log_print(f"GET array [double] {n}: {o}")
        return 0

    return -1


def param_provider_get_int_array(
        reader: Any,
        name: ctypes.c_char_p,
        n_elem: ctypes.POINTER(ctypes.c_int),
        val: ctypes.POINTER(ctypes.POINTER(ctypes.c_int))
        ) -> int:
    """
    Retrieve an integer array from the reader based on the provided name.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to retrieve.
    n_elem : ctypes.POINTER(ctypes.c_int)
        A pointer to store the number of elements in the array.
    val : ctypes.POINTER(ctypes.POINTER(ctypes.c_int))
        A pointer to store the retrieved array.

    Returns
    -------
    int
        0 if the array was found and retrieved successfully, -1 otherwise.
    """
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]
        if isinstance(o, list):
            o = np.ascontiguousarray(o)
        if not isinstance(o, np.ndarray) or o.dtype != int or not o.flags.c_contiguous:
            return -1

        n_elem[0] = ctypes.c_int(o.size)
        val[0] = o.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        log_print(f"GET array [int] {n}: {o}")
        return 0

    return -1


def param_provider_get_double_array_item(
        reader: Any,
        name: ctypes.c_char_p,
        index: int, val: ctypes.POINTER(ctypes.c_double)
        ) -> int:
    """
    Retrieve an item from a double array in the reader based on the provided name and index.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to retrieve.
    index : int
        The index of the array item to retrieve.
    val : ctypes.POINTER(ctypes.c_double)
        A pointer to store the retrieved double value.

    Returns
    -------
    int
        0 if the value was found and retrieved successfully, -1 otherwise.
    """
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]

        try:
            float_val = float(o)
        except TypeError:
            float_val = float(o[index])

        val[0] = ctypes.c_double(float_val)
        log_print(f"GET array [double] ({index}) {n}: {val[0]}")
        return 0

    return -1


def param_provider_get_int_array_item(
        reader: Any,
        name: ctypes.c_char_p,
        index: int, val: ctypes.POINTER(ctypes.c_int)
        ) -> int:
    """
    Retrieve an item from an integer array in the reader based on the provided name and index.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to retrieve.
    index : int
        The index of the array item to retrieve.
    val : ctypes.POINTER(ctypes.c_int)
        A pointer to store the retrieved integer value.

    Returns
    -------
    int
        0 if the value was found and retrieved successfully, -1 otherwise.
    """
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]

        try:
            int_val = int(o)
        except TypeError:
            int_val = int(o[index])

        val[0] = ctypes.c_int(int_val)
        log_print(f"GET array [int] ({index}) {n}: {val[0]}")
        return 0

    return -1


def param_provider_get_bool_array_item(
        reader: Any,
        name: ctypes.c_char_p,
        index: int, val: ctypes.POINTER(ctypes.c_uint8)
        ) -> int:
    """
    Retrieve an item from a boolean array in the reader based on the provided name and index.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to retrieve.
    index : int
        The index of the array item to retrieve.
    val : ctypes.POINTER(ctypes.c_uint8)
        A pointer to store the retrieved boolean value.

    Returns
    -------
    int
        0 if the value was found and retrieved successfully, -1 otherwise.
    """
    n = name.decode('utf-8')
    c = reader.current()

    if n in c:
        o = c[n]

        try:
            int_val = int(o)
        except TypeError:
            int_val = int(o[index])

        val[0] = ctypes.c_uint8(int_val)
        log_print(f"GET array [bool] ({index}) {n}: {bool(val[0])}")
        return 0

    return -1


def param_provider_get_string_array_item(
        reader: Any,
        name: ctypes.c_char_p,
        index: int, val: ctypes.POINTER(ctypes.c_char_p)
        ) -> int:
    """
    Retrieve an item from a string array in the reader based on the provided name and index.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to retrieve.
    index : int
        The index of the array item to retrieve.
    val : ctypes.POINTER(ctypes.c_char_p)
        A pointer to store the retrieved string value.

    Returns
    -------
    int
        0 if the value was found and retrieved successfully, -1 otherwise.
    """
    name_str = name.decode('utf-8')
    current_reader = reader.current()

    if name_str in current_reader:
        str_value = current_reader[name_str]
        if isinstance(str_value, bytes):
            bytes_val = str_value
        else:
            bytes_val = str_value[index]

        reader.buffer = bytes_val
        val[0] = ctypes.cast(reader.buffer, ctypes.c_char_p)
        log_print(f"GET array [string] ({index}) {name_str}: {reader.buffer.decode('utf-8')}")
        return 0

    return -1


def param_provider_exists(
        reader: Any,
        name: ctypes.c_char_p
        ) -> int:
    """
    Check if a given parameter name exists in the reader.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to check.

    Returns
    -------
    int
        1 if the name exists, 0 otherwise.
    """
    n = name.decode('utf-8')
    c = reader.current()

    log_print(f"EXISTS {n}: {n in c}")

    return 1 if n in c else 0


def param_provider_is_array(
        reader: Any,
        name: ctypes.c_char_p,
        res: ctypes.POINTER(ctypes.c_uint8)
        ) -> int:
    """
    Check if a given parameter is an array.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to check.
    res : ctypes.POINTER(ctypes.c_uint8)
        A pointer to store the result (1 if the parameter is an array, 0 otherwise).

    Returns
    -------
    int
        0 if the check was successful, -1 if the parameter does not exist.
    """
    n = name.decode('utf-8')
    c = reader.current()

    if n not in c:
        return -1

    o = c[n]
    res[0] = ctypes.c_uint8(1 if isinstance(o, (list, np.ndarray)) else 0)
    log_print(f"ISARRAY {n}: {bool(res[0])}")

    return 0


def param_provider_num_elements(
        reader: Any,
        name: ctypes.c_char_p
        ) -> int:
    """
    Get the number of elements in a given parameter if it is an array.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the parameter to check.

    Returns
    -------
    int
        The number of elements if the parameter is an array, 1 otherwise.
    """
    n = name.decode('utf-8')
    c = reader.current()

    if n not in c:
        return -1

    o = c[n]
    if isinstance(o, list):
        log_print(f"NUMELEMENTS {n}: {len(o)}")
        return len(o)
    elif isinstance(o, np.ndarray):
        log_print(f"NUMELEMENTS {n}: {o.size}")
        return o.size

    log_print(f"NUMELEMENTS {n}: 1")
    return 1


def param_provider_push_scope(
        reader: Any,
        name: ctypes.c_char_p
        ) -> int:
    """
    Push a new scope in the reader based on the provided name.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.
    name : ctypes.c_char_p
        The name of the scope to push.

    Returns
    -------
    int
        0 if the scope was successfully pushed, -1 otherwise.
    """
    n = name.decode('utf-8')

    if reader.push_scope(n):
        return 0
    else:
        return -1


def param_provider_pop_scope(reader: Any) -> int:
    """
    Pop the current scope from the reader.

    Parameters
    ----------
    reader : Any
        The reader object containing the current data scope.

    Returns
    -------
    int
        0 if the scope was successfully popped.
    """
    reader.pop_scope()
    return 0
