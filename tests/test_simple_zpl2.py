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

@pytest.fixture
def formatter():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return Formatter()


def test_comment(formatter):
    formatter.add_comment('Testing Comment')
    assert no_newline(formatter) == '^XA^FXTesting Comment^FS^XZ'


def test_fail():
    assert True == False
