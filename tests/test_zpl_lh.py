import pytest
from simple_zpl2 import ZPLDocument


def test_label_home():
    # Test value ranges
    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_label_home(-1, 0)
    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_label_home(32001, 0)
    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_label_home(0, -1)
    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_label_home(0, 32001)

    zdoc = ZPLDocument()
    zdoc.add_label_home()
    assert(zdoc.zpl_bytes == b'^XA\n^LH\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_label_home(10)
    assert(zdoc.zpl_bytes == b'^XA\n^LH10\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_label_home(10, 10)
    assert(zdoc.zpl_bytes == b'^XA\n^LH10,10\n^XZ')
