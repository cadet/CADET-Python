import copy
import json
import os
from pathlib import Path
import pprint
from typing import Optional, Any
import warnings

from addict import Dict
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import h5py
import numpy

import filelock
import contextlib


class H5:
    """
    A class for handling hierarchical HDF5 data structures and JSON representations.

    Attributes
    ----------
    root : Dict
        The root data structure holding the HDF5/JSON data.
    filename : Optional[str]
        Path to the HDF5 file.

    Methods
    -------
    transform(x: Any) -> Any
        Applies a transformation to the data before saving.
    inverse_transform(x: Any) -> Any
        Applies an inverse transformation to the data after loading.
    load(paths: Optional[List[str]] = None, update: bool = False, lock: bool = False) -> None
        Loads data from the specified HDF5 file.
    save(lock: bool = False) -> None
        Saves the current data to the specified HDF5 file.
    save_json(filename: Union[str, Path]) -> None
        Saves the current data to a JSON file.
    load_json(filename: Union[str, Path], update: bool = False) -> None
        Loads data from a JSON file.
    append(lock: bool = False) -> None
        Appends new keys to the HDF5 file without reading existing data.
    update(other: "H5") -> None
        Merges another H5 object's data with the current one.
    """

    pp = pprint.PrettyPrinter(indent=4)

    def transform(self, x: Any) -> Any:
        """
        Transform the data before saving.

        Parameters
        ----------
        x : Any
            Data to be transformed.

        Returns
        -------
        Any
            Transformed data.
        """
        return x

    def inverse_transform(self, x: Any) -> Any:
        """
        Apply an inverse transformation to the data after loading.

        Parameters
        ----------
        x : Any
            Data to be transformed back.

        Returns
        -------
        Any
            Inversely transformed data.
        """
        return x

    def __init__(self, *data: Any):
        """
        Initialize an H5 object with optional data.

        Parameters
        ----------
        data : Any
            Optional initial data to populate the object.
        """
        self.root = Dict()
        self.filename: Optional[str] = None
        for i in data:
            self.root.update(copy.deepcopy(i))

    def load(
            self,
            paths: Optional[list[str]] = None,
            update: bool = False,
            lock: bool = False
    ) -> None:
        """
        Load data from the specified HDF5 file.

        Parameters
        ----------
        paths : Optional[List[str]], optional
            Specific paths to load within the HDF5 file.
        update : bool, optional
            If True, update the existing data with the loaded data,
            i.e. keep existing data and ADD loaded data.
            If False, discard existing data and only keep loaded data.
        lock : bool, optional
            If True, uses a file lock while loading.
        """
        warnings.warn(
            "Deprecation warning: Support for `load` will be removed in a future "
            "version. Use `load_from_file` instead.",
            FutureWarning
        )
        self.load_from_file(paths=paths, update=update, lock=lock)

    def load_from_file(
            self,
            paths: Optional[list[str]] = None,
            update: bool = False,
            lock: bool = False
            ) -> None:
        """
        Load data from the specified HDF5 file.

        Parameters
        ----------
        paths : Optional[List[str]], optional
            Specific paths to load within the HDF5 file.
        update : bool, optional
            If True, update the existing data with the loaded data,
            i.e. keep existing data and ADD loaded data.
            If False, discard existing data and only keep loaded data.
        lock : bool, optional
            If True, uses a file lock while loading.
        """
        if self.filename is not None:
            lock_file = filelock.FileLock(
                    self.filename + '.lock'
                ) if lock else contextlib.nullcontext()

            with lock_file:
                with h5py.File(self.filename, 'r') as h5file:
                    data = Dict(
                        recursively_load(h5file, '/', self.inverse_transform, paths)
                    )
                    if update:
                        self.root.update(data)
                    else:
                        self.root = data
        else:
            print('Filename must be set before load can be used')

    def save(self, lock: bool = False) -> None:
        """
        Save the current data to the specified HDF5 file.

        Parameters
        ----------
        lock : bool, optional
            If True, uses a file lock while saving.

        Raises
        ------
        ValueError
            If the filename is not set before attempting to save.
        """
        if self.filename is not None:
            lock_file = filelock.FileLock(
                    self.filename + '.lock'
                ) if lock else contextlib.nullcontext()

            with lock_file:
                with h5py.File(self.filename, 'w') as h5file:
                    recursively_save(h5file, '/', self.root, self.transform)
        else:
            raise ValueError("Filename must be set before save can be used")

    def save_as_python_script(self, filename: str, only_return_pythonic_representation=False):
        if not filename.endswith(".py"):
            raise Warning(f"The filename given to .save_as_python_script isn't a python file name.")

        code_lines_list = [
            "import numpy",
            "from cadet import Cadet",
            "",
            "sim = Cadet()",
            "root = sim.root",
        ]

        code_lines_list = recursively_turn_dict_to_python_list(dictionary=self.root,
                                                               current_lines_list=code_lines_list,
                                                               prefix="root")

        filename_for_reproduced_h5_file = filename.replace(".py", ".h5")
        code_lines_list.append(f"sim.filename = '{filename_for_reproduced_h5_file}'")
        code_lines_list.append("sim.save()")

        if not only_return_pythonic_representation:
            with open(filename, "w") as handle:
                handle.writelines([line + "\n" for line in code_lines_list])
        else:
            return code_lines_list

    def delete_file(self) -> None:
        """Delete the file associated with the current instance."""
        if self.filename is not None:
            try:
                os.remove(self.filename)
            except FileNotFoundError:
                pass

    def save_json(self, filename: str | Path) -> None:
        """
        Save the current data to a JSON file.

        Parameters
        ----------
        filename : str | Path
            Path to the JSON file.
        """
        with Path(filename).open("w") as fp:
            data = convert_from_numpy(self.root, self.transform)
            json.dump(data, fp, indent=4, sort_keys=True)

    def load_json(self, filename: str | Path, update: bool = False) -> None:
        """
        Load data from a JSON file.

        Parameters
        ----------
        filename : str | Path
            Path to the JSON file.
        update : bool, optional
            If True, updates the existing data with the loaded data.
        """
        with Path(filename).open("r") as fp:
            data = json.load(fp)
            data = recursively_load_dict(data, self.inverse_transform)
            if update:
                self.root.update(data)
            else:
                self.root = data

    def append(self, lock: bool = False) -> None:
        """
        Append new keys to the HDF5 file without reading existing data.

        Parameters
        ----------
        lock : bool, optional
            If True, uses a file lock while appending.
        """
        if self.filename is not None:
            lock_file = filelock.FileLock(
                    self.filename + '.lock'
                ) if lock else contextlib.nullcontext()

            with lock_file:
                with h5py.File(self.filename, 'a') as h5file:
                    recursively_save(h5file, '/', self.root, self.transform)
        else:
            print("Filename must be set before save can be used")

    def __str__(self) -> str:
        """
        Return a string representation of the object.

        Returns
        -------
        str
            String representation of the filename and root data.
        """
        temp = []
        temp.append(f'Filename = {self.filename}')
        temp.append(self.pp.pformat(self.root))
        return '\n'.join(temp)

    def update(self, other: "H5") -> None:
        """
        Merge another H5 object's data with the current one.

        Parameters
        ----------
        other : H5
            Another H5 object whose data will be merged.
        """
        self.root.update(other.root)

    def __getitem__(self, key: str) -> Any:
        """
        Access data by key.

        Parameters
        ----------
        key : str
            Key for accessing nested data.

        Returns
        -------
        Any
            Retrieved data.
        """
        key = key.lower()
        obj = self.root
        for i in key.split('/'):
            if i:
                obj = obj[i]
        return obj

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set data by key.

        Parameters
        ----------
        key : str
            Key for accessing nested data.
        value : Any
            Value to set for the given key.
        """
        key = key.lower()
        obj = self.root
        parts = key.split('/')
        for i in parts[:-1]:
            if i:
                obj = obj[i]
        obj[parts[-1]] = value


def convert_from_numpy(data: Dict, func: Optional[callable] = None) -> Dict:
    """
    Convert a dictionary with NumPy objects into native Python types.

    Parameters
    ----------
    data : dict
        The input dictionary with potential NumPy types.
    func : callable
        A function to transform the keys.

    Returns
    -------
    dict
        A dictionary with transformed keys and native Python types.
    """
    ans = {}
    for key, item in data.items():
        if func is not None:
            key = func(key)

        # Handle NumPy-specific types
        if isinstance(item, numpy.ndarray):
            item = item.tolist()
        elif isinstance(item, numpy.generic):
            item = item.item()

        # Handle bytes
        elif isinstance(item, bytes):
            item = item.decode('utf-8')

        # Recursive handling of nested dictionaries
        if isinstance(item, dict):  # Assuming Dict is replaced with dict
            ans[key] = convert_from_numpy(item, func)
        else:
            ans[key] = item

    return ans


def recursively_load_dict(data: dict, func: Optional[callable] = None) -> Dict:
    """
    Recursively load data from a dictionary.

    Parameters
    ----------
    data : dict
        Input dictionary to load.
    func : callable
        Transformation function for dictionary keys.

    Returns
    -------
    Dict
        Dictionary with loaded data.
    """
    ans = Dict()
    for key, item in data.items():
        if func is not None:
            key = func(key)

        if isinstance(item, dict):
            ans[key] = recursively_load_dict(item, func)
        else:
            # Handle bytes
            if isinstance(item, numpy.int32):
                item = int(item)
            elif isinstance(item, bytes):
                item = item.decode('utf-8')

            ans[key] = item
    return ans


def set_path(obj: Dict[str, Any], path: str, value: Any) -> None:
    """
    Set a value within a nested dictionary given a slash-separated path.

    Parameters
    ----------
    obj : Dict[str, Any]
        Dictionary to set the value in.
    path : str
        Slash-separated path indicating where to set the value.
    value : Any
        Value to be set at the specified path.
    """
    path_parts = [i for i in path.split('/') if i]

    temp = obj
    for part in path_parts[:-1]:
        if part not in temp or not isinstance(temp[part], dict):
            temp[part] = {}  # Create intermediate dictionaries as needed
        temp = temp[part]

    value = recursively_load_dict(value)

    temp[path_parts[-1]] = value


def recursively_load(
        h5file: h5py.File,
        path: str,
        func: callable,
        paths: Optional[list[str]]
        ) -> Dict:
    """
    Recursively load data from an HDF5 file.

    Parameters
    ----------
    h5file : h5py.File
        The HDF5 file to load data from.
    path : str
        Path within the HDF5 file.
    func : callable
        Transformation function for dictionary keys.
    paths : Optional[List[str]]
        Specific paths to load, or None to load everything.

    Returns
    -------
    Dict
        Loaded data.
    """
    ans = Dict()
    if paths is not None:
        for path in paths:
            item = h5file.get(path, None)
            if item is not None:
                if isinstance(item, h5py._hl.dataset.Dataset):
                    set_path(ans, path, item[()])
                elif isinstance(item, h5py._hl.group.Group):
                    set_path(
                        ans, path, recursively_load(h5file, path + '/', func, None)
                    )
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


def recursively_save(h5file: h5py.File, path: str, dic: Dict, func: callable) -> None:
    """
    Recursively save data to an HDF5 file.

    Parameters
    ----------
    h5file : h5py.File
        The HDF5 file to save data to.
    path : str
        Path within the HDF5 file.
    dic : Dict
        Dictionary of data to save.
    func : callable
        Transformation function for dictionary keys.

    Raises
    ------
    ValueError
        If path or h5file types are invalid, or if the dictionary contains unsupported
        data types.
    """
    if not isinstance(path, str):
        raise ValueError("path must be a string")
    if not isinstance(h5file, h5py._hl.files.File):
        raise ValueError("must be an open h5py file")
    if not isinstance(dic, dict):
        raise ValueError("must provide a dictionary")

    for key, item in dic.items():
        key = str(key)

        if item is None:
            continue

        if not isinstance(key, str):
            raise ValueError("dict keys must be strings to save to hdf5")

        if isinstance(item, dict):
            recursively_save(h5file, path + key + '/', item, func)
            continue
        elif isinstance(item, str):
            value = numpy.array(item.encode('utf-8'))
        elif isinstance(item, list) and all(isinstance(i, str) for i in item):
            value = numpy.array([i.encode('utf-8') for i in item])
        else:
            try:
                value = numpy.array(item)
            except TypeError:
                raise ValueError(
                    f'Cannot save {path}/{func(key)} key with {type(item)} type.'
                )

        try:
            h5file[path + func(key)] = value
        except OSError as e:
            if str(e) == 'Unable to create link (name already exists)':
                raise KeyError(
                    'Name conflict with upper and lower case entries for key '
                    f'"{path}{key}".'
                )
            else:
                raise


def recursively_turn_dict_to_python_list(dictionary: dict, current_lines_list: list = None, prefix: str = None):
    """
    Recursively turn a nested dictionary or addict.Dict into a list of Python code that
    can generate the nested dictionary.

    :param dictionary:
    :param current_lines_list:
    :param prefix_list:
    :return: list of Python code lines
    """

    def merge_to_absolute_key(prefix, key):
        """
        Combine key and prefix to "prefix.key" except if there is no prefix, then return key
        """
        if prefix is None:
            return key
        else:
            return f"{prefix}.{key}"

    def clean_up_key(absolute_key: str):
        """
        Remove problematic phrases from key, such as blank "return"

        :param absolute_key:
        :return:
        """
        absolute_key = absolute_key.replace(".return", "['return']")
        return absolute_key

    def get_pythonic_representation_of_value(value):
        """
        Use repr() to get a pythonic representation of the value
        and add "np." to "array" and "float64"

        """
        value_representation = repr(value)
        value_representation = value_representation.replace("array", "numpy.array")
        value_representation = value_representation.replace("float64", "numpy.float64")
        try:
            eval(value_representation)
        except NameError as e:
            raise ValueError(
                f"Encountered a value of '{value_representation}' that can't be directly reproduced in python.\n"
                f"Please report this to the CADET-Python developers.") from e

        return value_representation

    if current_lines_list is None:
        current_lines_list = []

    for key in sorted(dictionary.keys()):
        value = dictionary[key]

        absolute_key = merge_to_absolute_key(prefix, key)

        if type(value) in (dict, Dict):
            current_lines_list = recursively_turn_dict_to_python_list(value, current_lines_list, prefix=absolute_key)
        else:
            value_representation = get_pythonic_representation_of_value(value)

            absolute_key = clean_up_key(absolute_key)

            current_lines_list.append(f"{absolute_key} = {value_representation}")

    return current_lines_list
