from simple_zpl2 import Formatter


zpl = Formatter()

zpl.add_comment('Create a QR Code')
zpl.add_field_origin(20, 20)
zpl.add_barcode_qr(1, 2, zpl.QR_ERROR_CORRECTION_STANDARD)
zpl.add_field_data('This is data inside a QR code.  This is a barcode often read by cell phones.')

zpl.add_comment('Now some text')
zpl.add_font('C', zpl.ORIENTATION_NORMAL, 15)
zpl.add_field_data('Text on Label')

# Print generated text
print(zpl.zpl_text)
