"""
Test general properties of Cadet.
"""


import re
import pytest
from cadet import Cadet


@pytest.mark.parametrize("use_dll", [True, False])
def test_version(use_dll):
    # Assuming Cadet has a method to set or configure the use of DLL
    cadet = Cadet(use_dll=use_dll)

    assert re.match(r"\d\.\d\.\d", cadet.version), "Version format should be X.X.X"


if __name__ == '__main__':
    pytest.main([__file__])
