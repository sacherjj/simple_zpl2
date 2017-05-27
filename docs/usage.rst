=====
Usage
=====

To use Simple ZPL2 in a project::

    from simple_zpl2 import Formatter

    # Each label is built with a Formatter object
    # The below code would generally be built into a method to create the object or both create and print.
    zpl = Formatter()
    zpl.add_field_origin(20, 20)
    zpl.add_barcode_qr(1, 2, zpl.QR_ERROR_CORRECTION_STANDARD)
    zpl.add_field_data('This is data inside a QR code.  This is a barcode often read by cell phones.')

You can view the zpl encoded text::

    print(zpl.zpl_text)

Using a web service to render the label as PNG::

    from PIL import Image
    import io

    # Get PNG byte array
    png = zpl.render_png(label_width=2, label_height=1)
    # render fake file from bytes
    fake_file = io.BytesIO(png)
    img = Image.open(fake_file)
    # Open image with the default image viewer on your system
    img.show()

Print label to network based label printer::

    from simple_zpl2 import NetworkPrinter

    prn = NetworkPrinter('192.168.40.1')
    prn.print_zpl(zpl)

