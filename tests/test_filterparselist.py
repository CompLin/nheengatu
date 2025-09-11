#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: September 8, 2025

import pytest
from Yauti import getparselist, filterparselist, AUX


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


def test_getparselist_and_filter_n_abs():
    parselist = getparselist('sinimú')
    result = filterparselist('N+ABS', parselist)
    assert result == [['sinimú', 'N+ABS+SG']]


def test_getparselist_and_filter_n_ncont():
    parselist = getparselist('sinimú')
    result = filterparselist('N+NCONT', parselist)
    assert result == [['sinimú', 'N+NCONT+SG']]


def test_getparselist_and_filter_abs():
    parselist = getparselist('sinimú')
    result = filterparselist('ABS', parselist)
    assert result == [['sinimú', 'N+ABS+SG']]

def test_getparselist_and_filter_abs_sg():
    parselist = getparselist('sinimú')
    result = filterparselist('ABS+SG', parselist)
    assert result == [['sinimú', 'N+ABS+SG']]


def test_getparselist_and_filter_ncont():
    parselist = getparselist('sinimú')
    result = filterparselist('NCONT', parselist)
    assert result == [['sinimú', 'N+NCONT+SG']]


def test_getparselist_and_filter_cont_raises():
    parselist = getparselist('sinimú')
    # Expect a ValueError since N+CONT does not appear in the parselist
    with pytest.raises(ValueError, match=r"N\+CONT"):
        filterparselist('N+CONT', parselist)

def test_getparselist_and_filter_N_sg_raises():
    parselist = getparselist('supiá')
    # Expect a ValueError since N+SG does not appear in the parselist
    with pytest.raises(ValueError, match=r"N\+SG"):
        filterparselist('N+SG', parselist)

# --- Tests for AUX lemmas ---

def test_filter_aux_reading_direct():
    # Example: 'aputari' → 'putari' as AUXN
    parselist = getparselist('aputari')
    result = filterparselist('AUXN', parselist)
    assert result == [['putari', 'AUXN']]


def test_filter_aux_case_insensitivity():
    parselist = getparselist('aputari')
    result_lower = filterparselist('auxn', parselist)
    result_upper = filterparselist('AUXN', parselist)
    assert result_lower == result_upper == [['putari', 'AUXN']]


def test_filter_aux_multiple_options():
    # Example with multiple AUX entries: 'yuíri' has AUXFS
    parselist = getparselist('yayuíri')
    # Pick the AUX reading
    result = filterparselist('AUXFS', parselist)
    assert result == [['yuíri', 'AUXFS']]


def test_filter_aux_nonexistent_tag_raises():
    parselist = getparselist('aputari')
    # No AUXFR for 'putari' → should raise ValueError
    with pytest.raises(ValueError, match="No parse found with tag 'AUXFR'"):
        filterparselist('AUXFR', parselist)
