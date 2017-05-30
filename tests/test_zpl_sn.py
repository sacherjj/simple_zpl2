import pytest
from simple_zpl2 import ZPLDocument


def test_serialization_data():
    zdoc = ZPLDocument()
    zdoc.add_serialization_data(111, 1)
    assert(zdoc.zpl_bytes == b'^XA\n^SN111,1,N\n^XZ')
    zdoc = ZPLDocument()
    zdoc.add_serialization_data(999999999999, -99999999999, 'Y')
    assert(zdoc.zpl_bytes == b'^XA\n^SN999999999999,-99999999999,Y\n^XZ')


def test_serialization_data_starting_error():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_serialization_data(1000000000000, 1)
    with pytest.raises(Exception):
        zdoc.add_serialization_data(-1, 1)
    with pytest.raises(Exception):
        zdoc.add_serialization_data('A', 1)


def test_serialization_data_change_error():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_serialization_data(1, 1000000000000)
    with pytest.raises(Exception):
        zdoc.add_serialization_data(1, -100000000000)
    with pytest.raises(Exception):
        zdoc.add_serialization_data(1, 'A')


def test_serialization_data_add_leading_error():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_serialization_data(1, 1, 'A')
    with pytest.raises(Exception):
        zdoc.add_serialization_data(1, 1, 1)
