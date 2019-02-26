from simple_zpl2 import ZPLDocument


def test_graphic_field(image):
    zdoc = ZPLDocument()
    zdoc.add_graphic_field(image, 1)
    assert zdoc.zpl_bytes == b'^XA\n^GFA,16,8,1,0000000000000000\n^XZ'

    zdoc = ZPLDocument()
    zdoc.add_graphic_field(image, 2, 2)
    expected = b'^XA\n^GFA,64,32,2,0000000000000000000000000000000000000000000000000000000000000000\n^XZ'
    assert zdoc.zpl_bytes == expected
