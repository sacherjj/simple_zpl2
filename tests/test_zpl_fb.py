import pytest
from simple_zpl2 import ZPLDocument


def test_field_block():
    zdoc = ZPLDocument()
    zdoc.add_field_block()
    assert(zdoc.zpl_bytes == b'^XA\n^FB0,1,0,L,0\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_field_block(1000)
    assert (zdoc.zpl_bytes == b'^XA\n^FB1000,1,0,L,0\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_field_block(100, 99)
    assert(zdoc.zpl_bytes == b'^XA\n^FB100,99,0,L,0\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_field_block(99, 98, -78)
    assert(zdoc.zpl_bytes == b'^XA\n^FB99,98,-78,L,0\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_field_block(111, 9999, -9999, 'C')
    assert(zdoc.zpl_bytes == b'^XA\n^FB111,9999,-9999,C,0\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_field_block(222, 1, 9999, 'R', 9999)
    assert(zdoc.zpl_bytes == b'^XA\n^FB222,1,9999,R,9999\n^XZ')


def test_field_block_error():
    for width in (-1, 'A', '', None):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_field_block(width=width)

    for lines in (0, 10000, 'A', '', None):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_field_block(max_lines=lines)

    for space in (-10000, 10000, 'A', '', None):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_field_block(dots_between_lines=space)

    for justify in (0, 'Q', '', None):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_field_block(text_justification=justify)

    for indent in (-1, 10000, 'B', '', None):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_field_block(hanging_indent=indent)
