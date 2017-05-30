import pytest
from simple_zpl2 import ZPLDocument


def test_field_origin():
    zdoc = ZPLDocument()
    zdoc.add_field_origin(1000, 999, 2)
    assert(zdoc.zpl_bytes == b'^XA\n^FO1000,999,2\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_field_origin()
    assert (zdoc.zpl_bytes == b'^XA\n^FO0,0\n^XZ')


def test_field_origin_error():
    for x_axis in (-1, 32001, 'E', '', None):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_field_origin(x_axis)

    for y_axis in (-1, 32001, 'E', '', None):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_field_origin(10, y_axis)

    for justification in (-1, 3, 'E'):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_field_origin(10, 10, justification)
