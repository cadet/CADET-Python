"""
Test general properties of Cadet.
"""

from pathlib import Path
import re
import pytest
from cadet import Cadet


@pytest.mark.parametrize("use_dll", [True, False])
def test_version(use_dll):
    # Assuming Cadet has a method to set or configure the use of DLL
    cadet = Cadet(use_dll=use_dll)

    assert re.match(r"\d\.\d\.\d", cadet.version), "Version format should be X.X.X"


@pytest.mark.parametrize("install_path", [
    pytest.param(None, id="conda"),
    pytest.param("pypi", id="pypi"),
])
def test_create_lwe_and_run_cli_smoke(install_path, tmp_path):
    """createLWE + cadet-cli smoke test for both the conda and the PyPI install."""
    if install_path == "pypi":
        cadet_core = pytest.importorskip("cadet_core")
        install_path = Path(cadet_core.__file__).parent
    else:
        install_path = Cadet.autodetect_cadet()

    cadet = Cadet(install_path=install_path, use_dll=False)

    model = cadet.create_lwe(file_path=tmp_path / "LWE.h5")
    return_information = model.run_simulation()

    assert return_information.return_code == 0


if __name__ == '__main__':
    pytest.main([__file__])
