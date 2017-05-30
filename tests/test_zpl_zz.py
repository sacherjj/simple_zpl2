import pytest
from simple_zpl2 import ZPLDocument


def test_printer_sleep():
    zdoc = ZPLDocument()
    zdoc.add_printer_sleep(10, 'Y')
    assert(zdoc.zpl_bytes == b'^XA\n^ZZ10,Y\n^XZ')


def test_printer_sleep_bad_sleep_seconds():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_printer_sleep('A', 'N')

    with pytest.raises(Exception):
        zdoc.add_printer_sleep(-1, 'N')


def test_printer_sleep_bad_shutdown_while_queued():
    zdoc = ZPLDocument()
    with pytest.raises(Exception):
        zdoc.add_printer_sleep(10, 'A')

    with pytest.raises(Exception):
        zdoc.add_printer_sleep(10, 12)
