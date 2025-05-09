import tempfile

import numpy as np
import pytest
from addict import Dict

from cadet import Cadet


@pytest.fixture
def original_model():
    """
    Create a new Cadet object for use in tests.
    """
    with tempfile.NamedTemporaryFile() as temp:
        model = Cadet().create_lwe(file_path=temp.name+".h5")
        model.run_simulation()
        yield model


def test_save_as_python(original_model):
    """
    Test saving and regenerating a Cadet model as Python code.

    Verifies that a Cadet model can be serialized to a Python script and
    accurately reconstructed by executing the generated script. This ensures
    that model parameters, including arrays and edge-case values, are preserved.

    Parameters
    ----------
    original_model : Cadet
        A Cadet model instance to populate and serialize for testing.

    Raises
    ------
    AssertionError
        If the regenerated model does not match the original model within
        a specified relative tolerance.
    """
    # initialize "model" variable to be overwritten by the exec lines later
    # it needs to be called "model", as that is the variable that the generated code overwrites
    model = Cadet()

    # Populate original_model with all tricky cases currently known
    original_model.root.input.foo = 1
    original_model.root.input.food = 1.9
    original_model.root.input.bar.baryon = np.arange(10)
    original_model.root.input.bar.barometer = np.linspace(0, 10, 9)
    original_model.root.input.bar.init_q = np.array([], dtype=np.float64)
    original_model.root.input.bar.init_qt = np.array([0., 0.0011666666666666668, 0.0023333333333333335])
    original_model.root.input.bar.par_disc_type = np.array([b'EQUIDISTANT_PAR'], dtype='|S15')
    original_model.root.input["return"].split_foobar = 1

    code_lines = original_model.save_as_python_script(
        filename="temp.py", only_return_pythonic_representation=True
    )

    # remove code lines that save the file
    code_lines = code_lines[:-2]

    # populate "sim" variable using the generated code lines
    for line in code_lines:
        exec(line)

    # test that "sim" is equal to "temp_cadet_file"
    recursive_equality_check(original_model.root, model.root, rtol=1e-5)


def recursive_equality_check(dict_a: dict, dict_b: dict, rtol=1e-5):
    """
    Recursively compare two nested dictionaries for equality.

    Compares the keys and values of two dictionaries. If a value is a nested
    dictionary, the function recurses. NumPy arrays are compared using
    `np.testing.assert_allclose`, except for byte strings which are compared
    directly.

    Parameters
    ----------
    dict_a : dict
        First dictionary to compare.
    dict_b : dict
        Second dictionary to compare.
    rtol : float, optional
        Relative tolerance for comparing NumPy arrays, by default 1e-5.

    Returns
    -------
    bool
        True if the dictionaries are equal; otherwise, an assertion is raised.

    Raises
    ------
    AssertionError
        If keys do not match, or values are not equal within the given tolerance.
    """
    assert dict_a.keys() == dict_b.keys()
    for key in dict_a.keys():
        value_a = dict_a[key]
        value_b = dict_b[key]
        if type(value_a) in (dict, Dict):
            recursive_equality_check(value_a, value_b)
        elif isinstance(value_a, np.ndarray):
            # This catches cases where strings are stored in arrays, and the dtype S15 causes numpy problems
            # which can happen if reading a simulation file back from an H5 file from disk
            if value_a.dtype == np.dtype("S15") and len(value_a) == 1 and len(value_b) == 1:
                assert value_a[0] == value_b[0]
            else:
                np.testing.assert_allclose(value_a, value_b, rtol=rtol)
        else:
            assert value_a == value_b
    return True


if __name__ == "__main__":
    pytest.main([__file__])
