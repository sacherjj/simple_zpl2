import pytest
from simple_zpl2 import ZPLDocument


def test_start_print():
    zdoc = ZPLDocument()
    zdoc.add_start_print(500)
    assert(zdoc.zpl_bytes == b'^XA\n^SP500\n^XZ')


def test_start_print_error():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_start_print(-1)

    with pytest.raises(Exception):
        zdoc.add_start_print(32001)
