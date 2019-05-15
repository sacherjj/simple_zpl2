import pytest
from simple_zpl2 import ZPLDocument


def test_graphic_box():
    zdoc = ZPLDocument()
    zdoc.add_graphic_box(3000)
    assert(zdoc.zpl_bytes == b'^XA\n^GB3000,1,1,B,0^FS\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_graphic_box(3000, 300)
    assert(zdoc.zpl_bytes == b'^XA\n^GB3000,300,1,B,0^FS\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_graphic_box(3000, 300, 3)
    assert(zdoc.zpl_bytes == b'^XA\n^GB3000,300,3,B,0^FS\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_graphic_box(3000, 300, 3, 'W')
    assert(zdoc.zpl_bytes == b'^XA\n^GB3000,300,3,W,0^FS\n^XZ')

    zdoc = ZPLDocument()
    zdoc.add_graphic_box(3000, 300, 3, 'W', 6)
    assert(zdoc.zpl_bytes == b'^XA\n^GB3000,300,3,W,6^FS\n^XZ')


def test_graphic_box_errors():
    for width in ('A', 0, 32001, '', None):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_graphic_box(width)

    # Test width vs thickness
    with pytest.raises(Exception):
        zdoc = ZPLDocument()
        zdoc.add_graphic_box(9, 200, 10)

    # Test height vs thickness
    with pytest.raises(Exception):
        zdoc = ZPLDocument()
        zdoc.add_graphic_box(200, 9, 10)

    for height in ('A', 0, 32001, '', None):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_graphic_box(100, height)

    for border in ('A', 0, 32001, '', None):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_graphic_box(32000, 32000, border)

    zdoc = ZPLDocument()
    for line_color in ('A', 2, '', None):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_graphic_box(100, 100, 1, line_color)

    for corner_rounding in ('A', -1, 9, '', None):
        with pytest.raises(Exception):
            zdoc = ZPLDocument()
            zdoc.add_graphic_box(100, 100, 1, 'W', corner_rounding)
