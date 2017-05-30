from simple_zpl2 import ZPLDocument, QR_Barcode


zpl = ZPLDocument()

zpl.add_comment('Create a QR Code')
zpl.add_field_origin(20, 20)
qr_data = 'This is data inside a QR code.  This is a barcode often read by cell phones.'
qr = QR_Barcode(qr_data, 2, 2, zpl.QR_ERROR_CORRECTION_STANDARD)
zpl.add_barcode(qr)

zpl.add_comment('Now some text')
zpl.add_field_origin(200, 20)
zpl.add_font('C', zpl.ORIENTATION_NORMAL, 15)
zpl.add_field_data('Text on Label')

# Print generated text
print(zpl.zpl_text)
