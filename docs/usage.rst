=====
Usage
=====

No effort has been made for backwards compatibility with Python 2.  I don't see the effort worth it for a new library.

Simple ZPL2 has a main object, the `ZPLDocument`.  This is used to build on the linear ZPL2 data.
For simpler fields, using the `.add_*` methods.  Larger barcode objects group these fields together for ease and data
validation.  These are added to the ZPLDocument via `.add_barcode` method.

To use Simple ZPL2 in a project::

    from simple_zpl2 import ZPLDocument, Code128_Barcode

    # Each label is built with a ZPLDocument object
    zdoc = ZPLDocument()
    zdoc.add_comment("Barcode and text")
    # zdoc.add_zpl_raw('^BY3')  # example of custom command; this ^BY command allows to change barcode width (default is 2, range is 1-10)
    zdoc.add_field_origin(20, 20)
    code128_data = 'TEST BARCODE'
    bc = Code128_Barcode(code128_data, 'N', 30, 'Y')
    zdoc.add_barcode(bc)

You can view the zpl encoded text::

    print(zdoc.zpl_text)

Using a web service to render the label as PNG::

    from PIL import Image
    import io

    # Get PNG byte array
    png = zdoc.render_png(label_width=2, label_height=1)
    # render fake file from bytes
    fake_file = io.BytesIO(png)
    img = Image.open(fake_file)
    # Open image with the default image viewer on your system
    img.show()

Print label to network based label printer::

    from simple_zpl2 import NetworkPrinter

    prn = NetworkPrinter('192.168.40.1')
    prn.print_zpl(zdoc)


Note: str vs bytes
------------------

There may currently be issues with using str instead of bytes for some portions of data.  I make the assumption
that the strings are in UTF-8 format.  Please file issues if you run into data errors due to this.  I will be converting
this to require bytes and add some helper methods for str input.
