import pytest
from simple_zpl2 import ZPLDocument


def test_field_data():
    zdoc = ZPLDocument()
    zdoc.add_field_data('data')
    assert(zdoc.zpl_bytes == b'^XA\n^FDdata^FS\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_field_data(['data', 'data2', 'data3'])
    assert(zdoc.zpl_bytes == b'^XA\n^FDdata^FSdata2^FSdata3^FS\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_field_data('data\ndata2')
    assert (zdoc.zpl_bytes == b'^XA\n^FDdata\ndata2^FS\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_field_data('data\ndata2', True)
    assert (zdoc.zpl_bytes == b'^XA\n^FDdata\\&data2^FS\n^XZ')

