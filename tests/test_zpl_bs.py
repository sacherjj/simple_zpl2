import pytest
from simple_zpl2 import ZPLDocument, UPC_EAN_Extensions_Barcode
from .util import *


def test_upc_ean_ext_barcode():
    zdoc = add_to_zdoc(UPC_EAN_Extensions_Barcode(12))
    assert(zdoc.zpl_bytes == b'^XA\n^BSN,100,Y,Y\n^FD12^FS\n^XZ')


def test_upc_ean_ext_barcode_errors():
    for data_value in ('', 111, 1111, 111111, 1111111):
        with pytest.raises(Exception):
            UPC_EAN_Extensions_Barcode(data_value)

    for orient in (-1, 10000, 'Q'):
        with pytest.raises(Exception):
            UPC_EAN_Extensions_Barcode('12334', orient)

    for height in (-1, 32001, 'Q'):
        with pytest.raises(Exception):
            UPC_EAN_Extensions_Barcode('12334', height=height)

    for print_line in (-1, 10000, 'Q'):
        with pytest.raises(Exception):
            UPC_EAN_Extensions_Barcode('12334', print_text=print_line)

    for print_above in (-1, 10000, 'Q'):
        with pytest.raises(Exception):
            UPC_EAN_Extensions_Barcode('12334', text_above=print_above)

