import pytest
from simple_zpl2 import ZPLDocument, GS1Databar_Barcode
from .util import *


def test_gs1_databar_barcode():
    zdoc = add_to_zdoc(GS1Databar_Barcode('123232'))
    assert(zdoc.zpl_bytes == b'^XA\n^BRR,1,3,1,25\n^FD123232^FS\n^XZ')

    zdoc = add_to_zdoc(GS1Databar_Barcode('123232', 'Extended Info'))
    assert(zdoc.zpl_bytes == b'^XA\n^BRR,1,3,1,25\n^FD123232|Extended Info^FS\n^XZ')

    zdoc = add_to_zdoc(GS1Databar_Barcode('123232', 'Extended Info', symbology_type=6))
    assert (zdoc.zpl_bytes == b'^XA\n^BRR,6,3,1,25,22\n^FD123232|Extended Info^FS\n^XZ')

    zdoc = add_to_zdoc(GS1Databar_Barcode('123232', 'Extended Info', 'I', 6, 10, 2, 400, 20))
    assert (zdoc.zpl_bytes == b'^XA\n^BRI,6,10,2,400,20\n^FD123232|Extended Info^FS\n^XZ')


def test_upc_ean_ext_barcode_errors():
    for orient in (-1, 10000, 'Q'):
        with pytest.raises(Exception):
            GS1Databar_Barcode('123321', orientation=orient)

    for symbology in (13, 0, 'Q', ''):
        with pytest.raises(Exception):
            GS1Databar_Barcode('123321', symbology_type=symbology)

    for magnification in (-1, 0, 11, 'Q', ''):
        with pytest.raises(Exception):
            GS1Databar_Barcode('123321', magnification=magnification)

    for sep_height in (-1, 0, 3, 'Q'):
        with pytest.raises(Exception):
            GS1Databar_Barcode('123321', separator_height=sep_height)

    for bar_height in (0, 32001, 'Q', ''):
        with pytest.raises(Exception):
            GS1Databar_Barcode('123321', bar_height=bar_height)

    for seg_width in (-1, 1, 23, 19, 'Q'):
        with pytest.raises(Exception):
            GS1Databar_Barcode('123321', symbology_type=6, segment_width=seg_width)

