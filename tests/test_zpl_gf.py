from simple_zpl2 import ZPLDocument


def test_graphic_field(image):
    zdoc = ZPLDocument()
    zdoc.add_graphic_field(image, 1)
    assert zdoc.zpl_bytes == b'^XA\n^GFA,2,1,1,00\n^XZ'

    zdoc = ZPLDocument()
    zdoc.add_graphic_field(image, 2, 2)
    expected = b'^XA\n^GFA,4,2,1,0000\n^XZ'
    assert zdoc.zpl_bytes == expected
