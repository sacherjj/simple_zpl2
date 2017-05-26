=====
Usage
=====

To use Simple ZPL2 in a project::

    from simple_zpl2 import Formatter, NetworkPrinter

    zpl = Formatter()
    zpl.add_field_origin(20, 20)
    zpl.add_barcode_qr(1, 2, zpl.QR_ERROR_CORRECTION_STANDARD)
    zpl.add_field_data('This is data inside a QR code.  This is a barcode often read by cell phones.')

    prn = NetworkPrinter('192.168.40.1')
    prn.print(zpl)
