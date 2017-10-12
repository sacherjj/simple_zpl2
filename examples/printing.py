from simple_zpl2 import ZPLDocument, QR_Barcode, NetworkPrinter


zpl = ZPLDocument()
printer = NetworkPrinter('192.168.49.43')  # CHANGE TO YOUR PRINTER IP

zpl.add_comment('Create a QR Code')
zpl.add_field_origin(20, 20)
qr_data = 'This is data inside a QR code.  This is a barcode often read by cell phones.'
qr = QR_Barcode(qr_data, 2, 2, zpl._QR_ERROR_CORRECTION_STANDARD)
zpl.add_barcode(qr)

zpl.add_comment('Now some text')
zpl.add_field_origin(200, 20)
zpl.add_font('C', zpl._ORIENTATION_NORMAL, 15)
zpl.add_field_data('Text on Label')

# Print generated text
printer.print_zpl(zpl)
