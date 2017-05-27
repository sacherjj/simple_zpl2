#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_simple_zpl2
----------------------------------

Tests for `simple_zpl2` module.
"""

import pytest

from contextlib import contextmanager

from simple_zpl2 import Formatter


def no_newline(formatter):
    return formatter.zpl_text.replace('\n', '')


def wrap(zpl):
    return '^XA' + zpl + '^XZ'


def char_range(a, b, inclusive=True):
    for c in range(ord(a), ord(b) + int(bool(inclusive))):
        yield chr(c)


def test_comment():
    zpl = Formatter()
    zpl.add_comment('Testing Comment')
    assert no_newline(zpl) == wrap('^FXTesting Comment^FS')


def test_add_font():
    for val in char_range('A', 'Z'):
        zpl = Formatter()
        zpl.add_font(val)
        assert(no_newline(zpl) == wrap('^A' + val))
    for val in char_range('0', '9'):
        zpl = Formatter()
        zpl.add_font(val)
        assert (no_newline(zpl) == wrap('^A' + val))
    for val in ('N', 'R', 'I', 'B'):
        zpl = Formatter()
        zpl.add_font('B', val)
        assert(no_newline(zpl) == wrap('^AB,' + val))
    for val in (10, 100, 32000):
        zpl = Formatter()
        zpl.add_font('B', 'N', val)
        assert(no_newline(zpl) == wrap('^AB,N,' + str(val)))
    for val in (10, 100, 32000):
        zpl = Formatter()
        zpl.add_font('B', 'N', 100, val)
        assert(no_newline(zpl) == wrap('^AB,N,100,' + str(val)))

    # Check Invalid values are raised
    with pytest.raises(ValueError):
        zpl = Formatter()
        zpl.add_font('A', '')
    for val in (9, 32001, -1):
        with pytest.raises(ValueError):
            zpl = Formatter()
            zpl.add_font('A', 'N', val)
        with pytest.raises(ValueError):
            zpl = Formatter()
            zpl.add_font('A', 'N', 10, val)


def test_label_home_range():
    # Test value ranges
    with pytest.raises(ValueError):
        zpl = Formatter()
        zpl.add_label_home(-1, 0)
    with pytest.raises(ValueError):
        zpl = Formatter()
        zpl.add_label_home(32001, 0)
    with pytest.raises(ValueError):
        zpl = Formatter()
        zpl.add_label_home(0, -1)
    with pytest.raises(ValueError):
        zpl = Formatter()
        zpl.add_label_home(0, 32001)

    zpl = Formatter()
    zpl.add_label_home()
    assert(no_newline(zpl) == wrap('^LH'))

    zpl = Formatter()
    zpl.add_label_home(10)
    assert(no_newline(zpl) == wrap('^LH10'))

    zpl = Formatter()
    zpl.add_label_home(10, 10)
    assert(no_newline(zpl) == wrap('^LH10,10'))

