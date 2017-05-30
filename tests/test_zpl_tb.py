import pytest
from simple_zpl2 import ZPLDocument


def test_text_blocks():
    zdoc = ZPLDocument()
    zdoc.add_text_blocks('N', 1000, 500)
    assert(zdoc.zpl_bytes == b'^XA\n^TBN,1000,500\n^XZ')


def test_text_blocks_bad_block_rotation():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_text_blocks('Z', 1000, 500)

    with pytest.raises(Exception):
        zdoc.add_text_blocks(2, 1000, 500)


def test_text_blocks_bad_block_width():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_text_blocks('N', 0, 500)

    with pytest.raises(Exception):
        zdoc.add_text_blocks('N', 'FC', 500)


def test_text_blocks_bad_block_height():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_text_blocks('N', 1000, 0)

    with pytest.raises(Exception):
        zdoc.add_text_blocks('N', 1000, 'ABC')
