from simple_zpl2 import ZPLDocument


def add_to_zdoc(upc):
    zdoc = ZPLDocument()
    zdoc.add_barcode(upc)
    return zdoc
