import pytest
from simple_zpl2 import ZPLDocument, UPC_A_Barcode
from .util import *


def test_upca_barcode():
    zdoc = add_to_zdoc(UPC_A_Barcode(1234, 'N', 30))
    assert(zdoc.zpl_bytes == b'^XA\n^BUN,30,Y,N,Y\n^FD00000001234^FS\n^XZ')

    zdoc = add_to_zdoc(UPC_A_Barcode('1234567891011', 'N', 30, 'N', 'Y', 'N'))
    assert (zdoc.zpl_bytes == b'^XA\n^BUN,30,N,Y,N\n^FD12345678910^FS\n^XZ')


def test_upca_barcode_errors():
    with pytest.raises(Exception):
        zdoc = add_to_zdoc(UPC_A_Barcode('0', 'N', 20))

    for orient in (-1, 10000, 'Q'):
        with pytest.raises(Exception):
            zdoc = add_to_zdoc(UPC_A_Barcode('12334', orient, 10))

    for height in (-1, 10000, 'Q'):
        with pytest.raises(Exception):
            zdoc = add_to_zdoc(UPC_A_Barcode('12334', 'N', height))

    for print_text in (-1, 10000, 'Q'):
        with pytest.raises(Exception):
            zdoc = add_to_zdoc(UPC_A_Barcode('12334', 'R', 10, print_text=print_text))

    for print_above in (-1, 10000, 'Q'):
        with pytest.raises(Exception):
            zdoc = add_to_zdoc(UPC_A_Barcode('12334', 'N', 10, text_above=print_above))

    for check in (-1, 10000, 'Q'):
        with pytest.raises(Exception):
            zdoc = add_to_zdoc(UPC_A_Barcode('12334', 'N', 10, check_digit=check))
