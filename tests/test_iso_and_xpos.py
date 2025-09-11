#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: September 11, 2025

import pytest
from AnnotateConllu import get_iso_code, checkXposTag

# ---------------------------------------
# TESTS FOR get_iso_code
# ---------------------------------------

valid_iso_codes = [
    "pt",    # Portuguese
    "PT",    # Portuguese
    "por",    # Portuguese
    "POR",    # Portuguese
    "eng",   # English
    "de",    # German
    "fra",   # French
    "es",    # Spanish
    "yrl",   # Nheengatu
    "gl",    # Galician
    "grc",   # Ancient Greek
    "deu",   # German
    "gae",   # Warekena
    "bwi",   # Baniwa
]

invalid_iso_codes = [
    "x",         # too short
    "abcd",      # too long
    "123",       # numeric
    "p@",        # invalid character
    "",          # empty string
    "yrl!",      # invalid punctuation
    "E",        # upper case only
    "français",  # non-ISO full name
]

@pytest.mark.parametrize("code", valid_iso_codes)
def test_get_iso_code_valid(code):
    """Valid ISO codes should not raise exceptions."""
    assert isinstance(get_iso_code(code), str)

@pytest.mark.parametrize("code", invalid_iso_codes)
def test_get_iso_code_invalid(code):
    """Invalid ISO codes should raise exceptions."""
    with pytest.raises(Exception):
        get_iso_code(code)

# ---------------------------------------
# TESTS FOR checkXposTag
# ---------------------------------------

valid_xpos_tags = [
    "n",
    "v",
    "ind",
    "a",
    "adva",
    "pron",
    "pron2",
    "v3",
    "v2",
    "demx",
    "DEMX"
]

invalid_xpos_tags = [
    "noun",     # lowercase
    "Vrb",      # partial casing
    "Verb!",    # punctuation
    "123",      # numeric
    "V ERB",    # space
    "",         # empty string
    "ADJ$",     # invalid symbol
]

@pytest.mark.parametrize("tag", valid_xpos_tags)
def test_checkXposTag_valid(tag):
    """Valid XPOS tags should not raise exceptions."""
    checkXposTag(tag)  # should not raise

@pytest.mark.parametrize("tag", invalid_xpos_tags)
def test_checkXposTag_invalid(tag):
    """Invalid XPOS tags should raise exceptions."""
    with pytest.raises(Exception):
        checkXposTag(tag)
