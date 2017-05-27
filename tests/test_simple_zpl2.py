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


@pytest.fixture
def formatter():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return Formatter()


def test_comment(formatter):
    formatter.add_comment('Testing Comment')
    stripped_text = formatter.zpl_text.replace('\n', '')
    assert stripped_text == '^XA^FXTesting Comment^FS^XZ'

