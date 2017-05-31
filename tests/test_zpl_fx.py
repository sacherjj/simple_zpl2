import pytest
from simple_zpl2 import ZPLDocument


def test_comment():
    zdoc = ZPLDocument()
    zdoc.add_comment('Testing Comment')
    assert zdoc.zpl_bytes == b'^XA\n^FXTesting Comment^FS\n^XZ'
