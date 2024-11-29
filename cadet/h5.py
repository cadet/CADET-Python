from typing import Optional, Union, Any, List
import copy
import json
import pprint
import warnings
from pathlib import Path

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

    def load(self, paths: Optional[List[str]] = None, update: bool = False, lock: bool = False) -> None:
        """
        Load data from the specified HDF5 file.

        Parameters
        ----------
        paths : Optional[List[str]], optional
            Specific paths to load within the HDF5 file.
        update : bool, optional
            If True, updates the existing data with the loaded data.
        lock : bool, optional
            If True, uses a file lock while loading.
        """
        if self.filename is not None:
            lock_file = filelock.FileLock(self.filename + '.lock') if lock else contextlib.nullcontext()

            with lock_file:
                with h5py.File(self.filename, 'r') as h5file:
                    data = Dict(recursively_load(h5file, '/', self.inverse_transform, paths))
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
        """
        if self.filename is not None:
            lock_file = filelock.FileLock(self.filename + '.lock') if lock else contextlib.nullcontext()

            with lock_file:
                with h5py.File(self.filename, 'w') as h5file:
                    recursively_save(h5file, '/', self.root, self.transform)
        else:
            print("Filename must be set before save can be used")

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
            lock_file = filelock.FileLock(self.filename + '.lock') if lock else contextlib.nullcontext()

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


def convert_from_numpy(data: Dict, func: Optional[callable]=None) -> Dict:
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


def recursively_load_dict(data: dict, func: Optional[callable]=None) -> Dict:
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


def recursively_load(h5file: h5py.File, path: str, func: callable, paths: Optional[List[str]]) -> Dict:
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
        If path or h5file types are invalid, or if the dictionary contains unsupported data types.
    """
    if not isinstance(path, str):
        raise ValueError("path must be a string")
    if not isinstance(h5file, h5py._hl.files.File):
        raise ValueError("must be an open h5py file")
    if not isinstance(dic, dict):
        raise ValueError("must provide a dictionary")

    for key, item in dic.items():
        key = str(key)
        value = None

        if not isinstance(key, str):
            raise ValueError("dict keys must be strings to save to hdf5")

        if isinstance(item, dict):
            recursively_save(h5file, path + key + '/', item, func)
        elif isinstance(item, str):
            value = numpy.array(item.encode('utf-8'))
        elif isinstance(item, list) and all(isinstance(i, str) for i in item):
            value = numpy.array([i.encode('utf-8') for i in item])
        else:
            try:
                value = numpy.array(item)
            except TypeError:
                raise ValueError(f'Cannot save {path}/{func(key)} key with {type(item)} type.')

        if value is not None:
            try:
                h5file[path + func(key)] = value
            except OSError as e:
                if str(e) == 'Unable to create link (name already exists)':
                    raise KeyError(f'Name conflict with upper and lower case entries for key "{path}{key}".')
                else:
                    raise
