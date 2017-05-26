from PIL import Image
import io
from simple_zpl2 import Formatter

# Build up ZPL label
zpl = Formatter()

zpl.add_comment("Barcode and text")
zpl.add_field_origin(20, 20)
zpl.add_barcode_code_128(zpl.ORIENTATION_NORMAL, 30, 'Y')
zpl.add_field_data('TEST BARCODE')

zpl.add_comment('Just Text')
zpl.add_field_origin(20, 100)
zpl.add_font('A', zpl.ORIENTATION_NORMAL, 15)
zpl.add_field_data('Just Text Here')

# Get PNG byte array
png = zpl.render_png(label_width=2, label_height=1)
# render fake file from bytes
fake_file = io.BytesIO(png)
img = Image.open(fake_file)
# Open image with the default image viewer on your system
img.show()

