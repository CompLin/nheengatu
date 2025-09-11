#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: July 18, 2025
import pytest
from Yauti import format_word

# Valid test cases
@pytest.mark.parametrize(
    "word_form, correct_form, word_tag, function_name, expected",
    [
        # No typo, no tag
        ('ne', '', '', '', 'ne'),
        # No typo, with tag
        ('ne', '', 'pron2', '', 'ne/pron2'),
        # Typo only
        ('n', 'ne', '', '', 'n/=typo:c|ne'),
        # Typo with tag
        ('n', 'ne', 'pron2', '', 'n/=typo:c|ne:x|pron2'),
        # Typo with tag and function
        ('n', 'ne', 'pron2', 'wm', 'n/=typo:c|ne:x|pron2:n|wm'),
        # Typo with function only
        ('n', 'ne', '', 'wm', 'n/=typo:c|ne:n|wm'),
    ]
)
def test_format_word_valid(word_form, correct_form, word_tag, function_name, expected):
    assert format_word(word_form, correct_form, word_tag, function_name) == expected

# Invalid inputs that should raise ValueError
@pytest.mark.parametrize(
    "word_form, correct_form",
    [
        ('', 'ne'),             # Missing word_form
        ('', ''),               # Completely empty
        ('ne', 'ne'),           # Typo mode with same word (invalid)
    ]
)
def test_format_word_invalid(word_form, correct_form):
    with pytest.raises(ValueError):
        format_word(word_form, correct_form)
