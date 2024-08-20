import os
from pathlib import Path

import pytest
import re

from cadet import Cadet

# Full path to cadet.dll or cadet.so, that is different from the system/conda cadet
full_path_dll = Path(r"C:\Users\ronal\Documents\CADET\out\install\aRELEASE\bin\cadet.dll")

install_path_conda = Cadet.autodetect_cadet()


def test_autodetection():
    sim = Cadet()
    assert sim.install_path == install_path_conda
    assert sim.cadet_dll_path.parent.parent == install_path_conda
    assert sim.cadet_cli_path.parent.parent == install_path_conda
    assert sim.cadet_runner.cadet_path.suffix not in [".dll", ".so"]


def test_install_path():
    sim = Cadet(install_path=full_path_dll, use_dll=True)
    assert sim.cadet_dll_path == full_path_dll
    assert sim.cadet_runner.cadet_path.suffix in [".dll", ".so"]

    sim = Cadet()
    sim.install_path = full_path_dll.parent.parent
    sim.use_dll = True
    assert sim.cadet_dll_path == full_path_dll
    assert sim.cadet_runner.cadet_path.suffix in [".dll", ".so"]

    sim = Cadet()
    with pytest.deprecated_call():
        sim.cadet_path = full_path_dll.parent.parent

    sim.use_dll = True
    assert sim.cadet_dll_path == full_path_dll
    assert sim.cadet_runner.cadet_path.suffix in [".dll", ".so"]


def test_dll_runner_attrs():
    cadet = Cadet(full_path_dll.parent.parent)
    cadet_runner = cadet._cadet_dll_runner
    assert re.match("\d\.\d\.\d", cadet_runner.cadet_version)
    assert isinstance(cadet_runner.cadet_branch, str)
    assert isinstance(cadet_runner.cadet_build_type, str | None)
    assert isinstance(cadet_runner.cadet_commit_hash, str)
    assert isinstance(cadet_runner.cadet_path, str | os.PathLike)


def test_cli_runner_attrs():
    cadet = Cadet(full_path_dll.parent.parent)
    cadet_runner = cadet._cadet_cli_runner
    assert re.match("\d\.\d\.\d", cadet_runner.cadet_version)
    assert isinstance(cadet_runner.cadet_branch, str)
    assert isinstance(cadet_runner.cadet_build_type, str | None)
    assert isinstance(cadet_runner.cadet_commit_hash, str)
    assert isinstance(cadet_runner.cadet_path, str | os.PathLike)


if __name__ == '__main__':
    pytest.main(["test_install_path_settings.py"])
