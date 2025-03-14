import pytest
import tempfile
import numpy as np
import json
import os
from pathlib import Path
from addict import Dict
import h5py
from cadet import H5
from cadet.h5 import recursively_save, recursively_load, convert_from_numpy, recursively_load_dict


@pytest.fixture
def h5_instance():
    return H5({
        "keyString": "value1",
        "keyInt": 42,
        "keyArray": np.array([1, 2, 3]),
        "keyNone": None,
        "keyDict": {
            "nestedKeyFloat": 12.345,
            "nestedKeyList": [1, 2, 3, 4],
            "nestedKeyNone": None,
        }
    })


@pytest.fixture
def temp_h5_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".h5") as tmp:
        yield tmp.name
    os.remove(tmp.name)


@pytest.fixture
def temp_json_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        yield tmp.name
    os.remove(tmp.name)


def test_init(h5_instance):
    assert isinstance(h5_instance.root, Dict)
    assert h5_instance.root.keyString == "value1"
    assert h5_instance.root.keyInt == 42


def test_save_and_load_h5(h5_instance, temp_h5_file):
    h5_instance.filename = temp_h5_file
    h5_instance.save()

    new_instance = H5()
    new_instance.filename = temp_h5_file
    new_instance.load_from_file()

    assert new_instance.root.keyString == b"value1"
    assert new_instance.root.keyInt == 42
    assert "keyNone" not in new_instance.root
    assert all(new_instance.root.keyDict["nestedKeyList"] == [1, 2, 3, 4])
    assert "nestedKeyNone" not in new_instance.root.keyDict
    assert np.array_equal(new_instance.root.keyArray, h5_instance.root.keyArray)


def test_save_and_load_json(h5_instance, temp_json_file):
    h5_instance.save_json(temp_json_file)

    new_instance = H5()
    new_instance.load_json(temp_json_file)

    assert new_instance.root.keyString == "value1"
    assert new_instance.root.keyInt == 42
    assert new_instance.root.keyArray == [1, 2, 3]


def test_append_data(h5_instance, temp_h5_file):
    h5_instance.filename = temp_h5_file
    h5_instance.save()

    h5_instance["key4"] = "new_value"

    with pytest.raises(KeyError):
        # This correctly raises a KeyError because h5_instance still contains
        # e.g. keyString and .append would try to over-write keyString
        h5_instance.append()

    addition_h5_instance = H5()
    addition_h5_instance.filename = temp_h5_file

    addition_h5_instance["key4"] = "new_value"
    addition_h5_instance.append()

    new_instance = H5()
    new_instance.filename = temp_h5_file
    new_instance.load_from_file()

    assert new_instance.root.key4 == b"new_value"


def test_update(h5_instance):
    other_instance = H5({"keyInt": 100, "key4": "added"})
    h5_instance.update(other_instance)

    assert h5_instance.root.keyInt == 100
    assert h5_instance.root.key4 == "added"


def test_recursively_save_and_load(h5_instance, temp_h5_file):
    data = Dict({"group": {"dataset": np.array([10, 20, 30])}})

    with h5py.File(temp_h5_file, "w") as h5file:
        recursively_save(h5file, "/", data, lambda x: x)

    with h5py.File(temp_h5_file, "r") as h5file:
        loaded_data = recursively_load(h5file, "/", lambda x: x, None)

    assert np.array_equal(loaded_data["group"]["dataset"], np.array([10, 20, 30]))


def test_transform_methods():
    instance = H5()
    data = np.array([1, 2, 3])

    transformed = instance.transform(data)
    inverse_transformed = instance.inverse_transform(transformed)

    assert np.array_equal(inverse_transformed, data)


def test_convert_from_numpy():
    data = Dict({"array": np.array([1, 2, 3]), "scalar": np.int32(10)})
    converted = convert_from_numpy(data)

    assert converted["array"] == [1, 2, 3]
    assert converted["scalar"] == 10


def test_recursively_load_dict():
    data = {"nested": {"value": np.int32(42), "bytes": b"text"}}
    loaded = recursively_load_dict(data)

    assert loaded.nested.value == 42
    assert loaded.nested.bytes == "text"


def test_get_set_item(h5_instance):
    h5_instance["key4"] = "test_value"
    assert h5_instance["key4"] == "test_value"

    h5_instance["nested/key5"] = 123
    assert h5_instance["nested/key5"] == 123


def test_string_representation(h5_instance):
    representation = str(h5_instance)
    assert "Filename = None" in representation
    assert "keyString" in representation
    assert "keyInt" in representation


def test_load_nonexistent_file():
    instance = H5()
    instance.filename = "nonexistent_file.h5"
    with pytest.raises(OSError):
        instance.load_from_file()


def test_save_without_filename(h5_instance):
    with pytest.raises(ValueError):
        h5_instance.save()


def test_load_json_with_invalid_data(temp_json_file):
    invalid_data = "{invalid_json: true}"
    Path(temp_json_file).write_text(invalid_data)

    instance = H5()
    with pytest.raises(json.JSONDecodeError):
        instance.load_json(temp_json_file)
