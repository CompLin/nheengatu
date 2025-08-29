#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: August 29, 2025

import pytest
from Yauti import getparselist, filterparselist


def test_filter_with_matching_tag():
    parselist = [['xirĩ', 'A'], ['xirĩ', 'V2']]
    result = filterparselist('A', parselist)
    assert result == [['xirĩ', 'A']]


def test_filter_with_nonmatching_tag_raises():
    parselist = [['xirĩ', 'A'], ['xirĩ', 'V2']]
    with pytest.raises(ValueError, match="No parse found with tag 'N'"):
        filterparselist('N', parselist)


def test_filter_with_empty_tag_returns_full_list():
    parselist = [['xirĩ', 'A'], ['xirĩ', 'V2']]
    result = filterparselist('', parselist)
    assert result == parselist


def test_filter_with_none_tag_returns_full_list():
    parselist = [['apigawa', 'N+SG'], ['apigawa', 'A']]
    result = filterparselist(None, parselist)
    assert result == parselist


def test_case_insensitivity():
    parselist = [['xirĩ', 'A'], ['xirĩ', 'V2']]
    result_lower = filterparselist('a', parselist)
    result_upper = filterparselist('A', parselist)
    assert result_lower == result_upper == [['xirĩ', 'A']]


# --- Tests using Yauti.getparselist("sinimú") ---

def test_getparselist_and_filter_sg():
    parselist = getparselist('sinimú')
    result = filterparselist('N+SG', parselist)
    assert result == [['sinimú', 'N+SG']]


def test_getparselist_and_filter_abs():
    parselist = getparselist('sinimú')
    result = filterparselist('N+ABS', parselist)
    assert result == [['sinimú', 'N+ABS+SG']]


def test_getparselist_and_filter_ncont():
    parselist = getparselist('sinimú')
    result = filterparselist('N+NCONT', parselist)
    assert result == [['sinimú', 'N+NCONT+SG']]


def test_getparselist_and_filter_cont_raises():
    parselist = getparselist('sinimú')
    # Expect a ValueError since N+CONT does not appear in the parselist
    with pytest.raises(ValueError, match=r"N\+CONT"):
        filterparselist('N+CONT', parselist)
