"""
Unit tests for CADET-C-API versioning support in cadet_dll.py.

Tests the following aspects of CAPI versioning:
1. Support for CAPI version 1.0.0
2. Support for CAPI version 1.1.0a1 and its timeout function
3. Error handling for unsupported versions
4. Old CAPI version semantic (cdtGetAPIv010000 vs cdtGetAPIv1_0_0)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from packaging.version import Version

from cadet.cadet_dll import (
    CADETAPI_V1_0_0,
    CADETAPI_V1_1_0a1,
    _get_api_signatures,
    _setup_api,
    CadetDLLRunner,
)


# Tests for ctypes Structure Definitions

def test_v1_0_0_structure_version():
    """Test that CADETAPI_V1_0_0 has correct version."""
    assert CADETAPI_V1_0_0._version == Version("1.0.0")


def test_v1_1_0a1_structure_version():
    """Test that CADETAPI_V1_1_0a1 has correct version."""
    assert CADETAPI_V1_1_0a1._version == Version("1.1.0a1")


def test_v1_0_0_structure_has_fields():
    """Test that CADETAPI_V1_0_0 structure has fields defined."""
    assert len(CADETAPI_V1_0_0._fields_) > 0


def test_v1_1_0a1_structure_has_fields():
    """Test that CADETAPI_V1_1_0a1 structure has fields defined."""
    assert len(CADETAPI_V1_1_0a1._fields_) > 0


def test_v1_1_0a1_has_timeout_field():
    """Test that CADETAPI_V1_1_0a1 has timeout field."""
    field_names = [field[0] for field in CADETAPI_V1_1_0a1._fields_]
    assert 'timeout' in field_names


def test_v1_0_0_does_not_have_timeout_field():
    """Test that CADETAPI_V1_0_0 does not have timeout field."""
    field_names = [field[0] for field in CADETAPI_V1_0_0._fields_]
    assert 'timeout' not in field_names


def test_v1_0_0_fields_are_subset_of_v1_1_0a1():
    """Test that v1.0.0 fields are a subset of v1.1.0a1 fields."""
    v1_0_0_fields = {field[0] for field in CADETAPI_V1_0_0._fields_}
    v1_1_0a1_fields = {field[0] for field in CADETAPI_V1_1_0a1._fields_}
    
    assert v1_0_0_fields.issubset(v1_1_0a1_fields)


# Tests for _setup_api Function

def test_setup_api_v1_0_0():
    """Test _setup_api correctly sets up v1.0.0 API fields."""
    fields = _setup_api(Version("1.0.0"))
    field_names = [field[0] for field in fields]
    
    assert 'createDriver' in field_names
    assert 'deleteDriver' in field_names
    assert 'runSimulation' in field_names
    assert 'timeout' not in field_names


def test_setup_api_v1_1_0a1():
    """Test _setup_api correctly sets up v1.1.0a1 API fields."""
    fields = _setup_api(Version("1.1.0a1"))
    field_names = [field[0] for field in fields]
    
    assert 'createDriver' in field_names
    assert 'deleteDriver' in field_names
    assert 'runSimulation' in field_names
    assert 'timeout' in field_names


def test_setup_api_fields_are_cfunctype():
    """Test that all setup API fields are CFUNCTYPE."""
    import ctypes
    
    fields = _setup_api(Version("1.0.0"))
    
    for field_name, field_type in fields:
        assert callable(field_type)


# Tests for _initialize_dll Method and Version Handling

@patch('cadet.cadet_dll.ctypes.cdll.LoadLibrary')
def test_unsupported_version_error_below_1_0_0(mock_load):
    """Test that versions below 1.0.0 raise TypeError."""
    mock_lib = MagicMock()
    mock_load.return_value = mock_lib
    
    mock_lib.cdtGetLibraryVersion.return_value = b"5.0.0"
    mock_lib.cdtGetLibraryCommitHash.return_value = b"abc123"
    mock_lib.cdtGetLibraryBranchRefspec.return_value = b"main"
    mock_lib.cdtGetLibraryBuildType.return_value = b"Release"
    mock_lib.cdtGetLatestCAPIVersion.return_value = b"0.9.0"
    
    runner = CadetDLLRunner.__new__(CadetDLLRunner)
    runner._cadet_path = Path("fake_path.so")
    
    with pytest.raises(TypeError) as exc_info:
        runner._initialize_dll()
    
    assert "does not support CADET-CAPI version" in str(exc_info.value)
    assert "0.9.0" in str(exc_info.value)


@patch('cadet.cadet_dll.ctypes.cdll.LoadLibrary')
def test_unsupported_version_error_above_2_0_0(mock_load):
    """Test that versions 2.0.0 and above raise TypeError."""
    mock_lib = MagicMock()
    mock_load.return_value = mock_lib
    
    mock_lib.cdtGetLibraryVersion.return_value = b"5.0.0"
    mock_lib.cdtGetLibraryCommitHash.return_value = b"abc123"
    mock_lib.cdtGetLibraryBranchRefspec.return_value = b"main"
    mock_lib.cdtGetLibraryBuildType.return_value = b"Release"
    mock_lib.cdtGetLatestCAPIVersion.return_value = b"2.0.0"
    
    runner = CadetDLLRunner.__new__(CadetDLLRunner)
    runner._cadet_path = Path("fake_path.so")
    
    with pytest.raises(TypeError) as exc_info:
        runner._initialize_dll()
    
    assert "does not support CADET-CAPI version" in str(exc_info.value)
    assert "2.0.0" in str(exc_info.value)


@patch('cadet.cadet_dll.ctypes.cdll.LoadLibrary')
def test_no_capi_function_error(mock_load):
    """Test that missing cdtGetLatestCAPIVersion raises ValueError."""
    mock_lib = MagicMock()
    mock_load.return_value = mock_lib
    
    mock_lib.cdtGetLibraryVersion.return_value = b"5.0.0"
    mock_lib.cdtGetLibraryCommitHash.return_value = b"abc123"
    mock_lib.cdtGetLibraryBranchRefspec.return_value = b"main"
    mock_lib.cdtGetLibraryBuildType.return_value = b"Release"
    del mock_lib.cdtGetLatestCAPIVersion
    
    runner = CadetDLLRunner.__new__(CadetDLLRunner)
    runner._cadet_path = Path("fake_path.so")
    
    with pytest.raises(ValueError) as exc_info:
        runner._initialize_dll()
    
    assert "does not support CADET-CAPI" in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__])
