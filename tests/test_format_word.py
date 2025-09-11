#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: July 18, 2025
import unittest

from Yauti import format_word


class TestFormatWord(unittest.TestCase):
    def test_no_tag_no_typo(self):
        self.assertEqual(format_word('ne'), 'ne')
        
    def test_no_tag_no_typo_with_empty_strings(self):
        self.assertEqual(format_word('ne','','',''), 'ne')

    def test_tag_no_typo(self):
        self.assertEqual(format_word('ne', word_tag='pron2'), 'ne/pron2')

    def test_tag_no_typo_with_empty_strings(self):
        self.assertEqual(format_word('ne', '',word_tag='pron2',function_name=''), 'ne/pron2')

    def test_typo_only(self):
        self.assertEqual(format_word('n', 'ne'), 'n/=typo:c|ne')

    def test_typo_with_tag(self):
        self.assertEqual(format_word('n', 'ne', 'pron2'), 'n/=typo:c|ne:x|pron2')

    def test_typo_with_tag_and_function(self):
        self.assertEqual(format_word('n', 'ne', 'pron2', 'wm'), 'n/=typo:c|ne:x|pron2:n|wm')

    def test_typo_with_function_only(self):
        self.assertEqual(format_word('n', 'ne', function_name='wm'), 'n/=typo:c|ne:n|wm')

    def test_empty_word_form(self):
        with self.assertRaises(ValueError):
            format_word('', 'ne')

if __name__ == '__main__':
    unittest.main()
