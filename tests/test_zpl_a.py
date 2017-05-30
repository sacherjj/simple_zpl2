import pytest
from simple_zpl2 import ZPLDocument


def test_add_font():
    zdoc = ZPLDocument()
    zdoc.add_font('A')
    assert(zdoc.zpl_bytes == b'^XA\n^AA\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_font('Y')
    assert(zdoc.zpl_bytes == b'^XA\n^AY\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_font(3)
    assert(zdoc.zpl_bytes == b'^XA\n^A3\n^XZ')

    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font('a')

    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font(23)


def test_add_font_orientation():
    for val in ('N', 'R', 'I', 'B'):
        zdoc = ZPLDocument()
        zdoc.add_font('B', val)
        assert(zdoc.zpl_bytes == b'^XA\n^AB,' + val.encode('utf-8') + b'\n^XZ')

    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font('A', '')

    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font('A', 7)


def test_add_font_height():
    for val in (10, 100, 32000):
        zdoc = ZPLDocument()
        zdoc.add_font('B', 'N', val)
        assert(zdoc.zpl_bytes == b'^XA\n^AB,N,' + str(val).encode('utf-8') + b'\n^XZ')

    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font('A', 'N', 9)

    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font('A', 'N', 32001)

    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font('A', 'N', 'ABC')


def test_add_font_width():
    for val in (10, 100, 32000):
        zdoc = ZPLDocument()
        zdoc.add_font('B', 'N', 100, val)
        assert(zdoc.zpl_bytes == b'^XA\n^AB,N,100,' + str(val).encode('utf-8') + b'\n^XZ')

    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font('A', 'N', 20, 9)

    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font('A', 'N', 20, 32001)

    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font('A', 'N', 20, 'ABC')
