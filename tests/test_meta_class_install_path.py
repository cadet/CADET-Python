from pathlib import Path
import pytest

from cadet import Cadet


""" These tests require two distinct CADET installations to compare between and should not run in the CI"""

# Full path to cadet.dll or cadet.so, that is different from the system/conda cadet
full_path_dll = Path("path/to/cadet")

install_path_conda = Cadet.autodetect_cadet()


@pytest.mark.local
def test_meta_class():
    Cadet.cadet_path = full_path_dll
    assert Cadet.use_dll

    # With a path set in the meta class, the sim instance should not autodetect and use the meta class cadet path
    sim = Cadet()
    assert sim.use_dll
    assert sim.install_path == full_path_dll.parent.parent
    assert sim.cadet_dll_path == full_path_dll
    assert sim.cadet_cli_path.parent.parent == full_path_dll.parent.parent

    # With an install path given, the sim instance should use the given install path
    sim = Cadet(install_path=install_path_conda)
    assert sim.install_path == install_path_conda
    assert sim.cadet_dll_path.parent.parent == install_path_conda
    assert sim.cadet_cli_path.parent.parent == install_path_conda

    # Reset Path
    Cadet.cadet_path = None


if __name__ == "__main__":
    pytest.main([__file__])
