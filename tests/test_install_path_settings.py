import warnings
from pathlib import Path

import pytest

from cadet import Cadet

full_path_dll = Path(r"C:\Users\ronal\Documents\CADET\out\install\aRELEASE\bin\cadet.dll")
install_path_dll = full_path_dll.parent.parent

install_path_conda = Cadet.autodetect_cadet()


def test_autodetection():
    sim = Cadet()
    assert sim.install_path == install_path_conda
    assert sim.cadet_dll_path.parent.parent == install_path_conda
    assert sim.cadet_cli_path.parent.parent == install_path_conda
    assert sim.cadet_runner.cadet_path.suffix != "dll"


def test_install_path():
    sim = Cadet(install_path=full_path_dll, use_dll=True)
    assert sim.cadet_dll_path == full_path_dll
    assert sim.cadet_runner.cadet_path.suffix == ".dll"

    sim = Cadet()
    sim.install_path = full_path_dll.parent.parent
    sim.use_dll = True
    assert sim.cadet_dll_path == full_path_dll
    assert sim.cadet_runner.cadet_path.suffix == ".dll"

    sim = Cadet()
    with pytest.deprecated_call():
        sim.cadet_path = full_path_dll.parent.parent

    sim.use_dll = True
    assert sim.cadet_dll_path == full_path_dll
    assert sim.cadet_runner.cadet_path.suffix == ".dll"


def test_meta_class():
    Cadet.cadet_path = full_path_dll
    assert Cadet.use_dll

    # With a path set in the meta class, the sim instance should not autodetect and use the meta class cadet path
    sim = Cadet()
    assert sim.use_dll
    assert sim.install_path == install_path_dll
    assert sim.cadet_dll_path.parent.parent == install_path_dll
    assert sim.cadet_cli_path.parent.parent == install_path_dll

    # With an install path given, the sim instance should use the given install path
    sim = Cadet(install_path=install_path_conda)
    assert sim.install_path == install_path_conda
    assert sim.cadet_dll_path.parent.parent == install_path_conda
    assert sim.cadet_cli_path.parent.parent == install_path_conda
