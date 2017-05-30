#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_simple_zpl2
----------------------------------

Tests for `simple_zpl2` module.
"""

import pytest
from simple_zpl2 import *


def no_newline(formatter):
    return formatter.zpl_text.replace('\n', '')


def wrap(zpl):
    return '^XA' + zpl + '^XZ'


def char_range(a, b, inclusive=True):
    for c in range(ord(a), ord(b) + int(bool(inclusive))):
        yield chr(c)





