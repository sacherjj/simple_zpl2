import pytest
from simple_zpl2 import ZPLDocument


def test_graphic_circle():
    zdoc = ZPLDocument()
    zdoc.add_graphic_circle(3999)
    assert(zdoc.zpl_bytes == b'^XA\n^GC3999,1,B^FS\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_graphic_circle(3999, 234)
    assert(zdoc.zpl_bytes == b'^XA\n^GC3999,234,B^FS\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_graphic_circle(3999, 234, 'W')
    assert(zdoc.zpl_bytes == b'^XA\n^GC3999,234,W^FS\n^XZ')


def test_graphic_circle_errors():
    zdoc = ZPLDocument()
    with pytest.raises(ValueError):
        for val in ('A', 2, 4096, '', None):
            zdoc.add_graphic_circle(val)

    with pytest.raises(ValueError):
        for val in ('A', 0, 4096, '', None):
            zdoc.add_graphic_circle(100, val)

    with pytest.raises(ValueError):
        for val in ('A', 3, '', None):
            zdoc.add_graphic_circle(100, 2, val)
