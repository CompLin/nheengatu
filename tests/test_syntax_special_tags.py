#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: September 11, 2025
import unittest
from lark import exceptions
from LarkTagValidator import parser, TagTransformer
from LarkTagValidator import validate_special_tag

class TestSpecialTagParsing(unittest.TestCase):
    def setUp(self):
        self.valid = [
            "@",
            "a",
            "adva",
            "n+abs",
            "a@",
            "n+abs@",
            "=mid",
            "=mid@",
            "=typo:c|puranga",
            "=typo:c|puranga:x|adva",
            "=typo:c|puranga:x|adva@",
            "=custom:arg1|val1:arg2|val2",
            "=custom:arg1|a+b:arg2|val2",
            "=custom:arg1|a+b:arg2|c+d",
            "=custom:arg1|val1:arg2|val2@",
        ]
        self.invalid = [
           "c|puranga:x=typo",     # function name after argument value pair
         "arg1|val1",            # argument value pair without function name
         "arg1|val1:arg2|val2",  # multiple argument value pairs without function name
         ":arg1|val1:arg2|val2",
         "=:arg1|val1:arg2|val2",
         "=arg1|val1:arg2|val2",
         "=typo:c|puranga:x|adva:", # trailing colon
          "=typo::c|puranga:x|adva", # multiple colons in sequence
          "=typo:c|puranga::x|adva", # multiple colons in sequence
          "typo:c|puranga", # missing equal sign
        "=typo:c|puranga:x",     # x has no value
        "=typo:c|puranga:x|",    # trailing |
        "=typo:c|",              # no val
        "=typo:|puranga",        # no arg
        "=",                     # empty func
        "=:",                    # invalid
        "=typo:c|puranga:x||adva",    # double separator
        "a/b",                   # slash present
        "n++abs",                # invalid double +
         "n+",                # trailing +
         "n++",                # trailing +
         "@a",
        "@n+abs",
        "@n+abs@",
        "n@+abs",
        "n+@abs",
        "=@mid",
        "=@mid@",
        "n-abs",                # invalid -
        "n_abs",                # invalid _
        "n-+abs",                # invalid double -+
        "n:abs",                # invalid :
        ]
        self.parser = parser
        self.transformer = TagTransformer()

    def test_valid_tags(self):
        for tag in self.valid:
            with self.subTest(tag=tag):
                self.assertTrue(validate_special_tag(tag), f"Should validate: {tag}")
                tree = self.parser.parse(tag)
                result = self.transformer.transform(tree)
                self.assertIsInstance(result, dict)

    def test_invalid_tags(self):
        for tag in self.invalid:
            with self.subTest(tag=tag):
                self.assertFalse(validate_special_tag(tag), f"Should fail validation: {tag}")
                with self.assertRaises(exceptions.LarkError, msg=f"Should raise parse error for: {tag}"):
                    self.parser.parse(tag)

if __name__ == '__main__':
    unittest.main()
