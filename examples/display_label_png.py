from PIL import Image
import io
from simple_zpl2 import ZPLDocument, Code128_Barcode

# Build up ZPL label
zpl = ZPLDocument()

zpl.add_comment("Barcode and text")
zpl.add_field_origin(20, 20)
code128_data = 'TEST BARCODE'
bc = Code128_Barcode(code128_data, zpl._ORIENTATION_NORMAL, 30, 'Y')
zpl.add_barcode(bc)

zpl.add_comment('Just Text')
zpl.add_field_origin(20, 100)
zpl.add_font('A', zpl._ORIENTATION_NORMAL, 15)
zpl.add_field_data('Just Text Here')

# Get PNG byte array
png = zpl.render_png(label_width=2, label_height=1)
# render fake file from bytes
fake_file = io.BytesIO(png)
img = Image.open(fake_file)
# Open image with the default image viewer on your system
img.show()

