import pytest
from simple_zpl2 import ZPLDocument


def test_print_quantity():
    zdoc = ZPLDocument()
    zdoc.add_print_quantity(4)
    assert(zdoc.zpl_bytes == b'^XA\n^PQ4,0,0,N,Y\n^XZ')


def text_print_quantity_pause():
    zdoc = ZPLDocument()
    zdoc.add_print_quantity(4, 5)
    assert (zdoc.zpl_bytes == b'^XA\n^PQ4,5,0,N,Y\n^XZ')


def text_print_quantity_replicates():
    zdoc = ZPLDocument()
    zdoc.add_print_quantity(1000, 22, 901)
    assert (zdoc.zpl_bytes == b'^XA\n^PQ1000,22,901,N,Y\n^XZ')


def text_print_quantity_override():
    zdoc = ZPLDocument()
    zdoc.add_print_quantity(1000, 22, 901, 'Y')
    assert (zdoc.zpl_bytes == b'^XA\n^PQ1000,22,901,Y,Y\n^XZ')


def text_print_quantity_cut_on_error():
    zdoc = ZPLDocument()
    zdoc.add_print_quantity(1000, 22, 901, 'Y', 'N')
    assert (zdoc.zpl_bytes == b'^XA\n^PQ1000,22,901,Y,N\n^XZ')


def test_print_quantity_range():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_print_quantity(0)
    with pytest.raises(Exception):
        zdoc.add_print_quantity('A')
    with pytest.raises(Exception):
        zdoc.add_print_quantity(100000000)


def test_print_quantity_pause_error():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_print_quantity(1, -1)
    with pytest.raises(Exception):
        zdoc.add_print_quantity(1, 'A')
    with pytest.raises(Exception):
        zdoc.add_print_quantity(1, 100000000)


def test_print_quantity_replicates_error():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_print_quantity(1, 0, -1)
    with pytest.raises(Exception):
        zdoc.add_print_quantity(1, 0, 'A')
    with pytest.raises(Exception):
        zdoc.add_print_quantity(1, 0, 100000000)


def test_print_quantity_override_error():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_print_quantity(1, 0, 0, 'A')
    with pytest.raises(Exception):
        zdoc.add_print_quantity(1, 0, 0, 10)


def test_print_quantity_cut_on_error_error():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_print_quantity(1, 0, 0, 'N', 1)
    with pytest.raises(Exception):
        zdoc.add_print_quantity(1, 0, 0, 'N', 'A')
