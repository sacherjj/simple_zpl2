import pytest
from simple_zpl2 import ZPLDocument


@pytest.mark.parametrize("value", ("A", "Y", "3"))
def test_add_font(value):
    zdoc = ZPLDocument()
    zdoc.add_font(value)
    assert zdoc.zpl_bytes == b"^XA\n^A" + value.encode("utf-8") + b"\n^XZ"


@pytest.mark.parametrize("value", ("a", "", None, 73))
def test_add_font_with_invalid_value(value):
    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font(value)


@pytest.mark.parametrize("orientation", ("N", "R", "I", "B"))
def test_add_font_orientation(orientation):
    zdoc = ZPLDocument()
    zdoc.add_font("B", orientation)
    assert zdoc.zpl_bytes == b"^XA\n^AB" + orientation.encode("utf-8") + b"\n^XZ"


@pytest.mark.parametrize("orientation", ("F", "r", "", 7))
def test_add_font_with_invalid_orientation(orientation):
    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font("A", orientation)


@pytest.mark.parametrize("height", (10, 100, 32000))
def test_add_font_height(height):
    zdoc = ZPLDocument()
    zdoc.add_font("B", "N", height)
    assert zdoc.zpl_bytes == b"^XA\n^ABN," + str(height).encode("utf-8") + b"\n^XZ"


@pytest.mark.parametrize("height", (9, 32001, "ABC"))
def test_add_font_with_invalid_height(height):
    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font("A", "N", height)


@pytest.mark.parametrize("width", (10, 100, 32000))
def test_add_font_width(width):
    zdoc = ZPLDocument()
    zdoc.add_font("B", "N", 100, width)
    assert zdoc.zpl_bytes == b"^XA\n^ABN,100," + str(width).encode("utf-8") + b"\n^XZ"


@pytest.mark.parametrize("width", (9, 32001, "ABC"))
def test_add_font_with_invalid_width(width):
    with pytest.raises(ValueError):
        zdoc = ZPLDocument()
        zdoc.add_font("A", "N", 20, width)
