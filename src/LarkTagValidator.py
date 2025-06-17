#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: June 11, 2025
from lark import Lark, Transformer, UnexpectedInput, v_args

grammar = r"""
// Entry point
special_tag : root_only
            | tag_only
            | tag_with_root
            | func_only
            | func_with_args
            | func_with_root
            | func_with_args_and_root

TAG        : /[a-z]+[0-9]?(\+[a-z]+)*/
FUNC       : /[a-z]+/
ARGNAME    : /[a-z][a-z0-9]*/
VALUE      : /[\w\-\u00C0-\u024F]+/
ARGVAL     : ARGNAME "|" VALUE

root_only                  : "@"
tag_only                   : TAG
tag_with_root              : TAG "@"
func_only                  : "=" FUNC
func_with_args             : "=" FUNC ":" ARGVAL (":" ARGVAL)*
func_with_root             : "=" FUNC "@"
func_with_args_and_root    : "=" FUNC ":" ARGVAL (":" ARGVAL)* "@"

%ignore " "
"""

parser = Lark(grammar, start="special_tag", parser="lalr")


def _validate_special_tag(tag: str) -> bool:
    try:
        parser.parse(tag)
        return True
    except UnexpectedInput:
        return False


def validate_or_raise(tag: str) -> None:
    if not _validate_special_tag(tag):
        raise ValueError(f"Invalid tag format: {tag}")


@v_args(inline=True)
class TagTransformer(Transformer):
    def special_tag(self, item):
        return item

    def root_only(self):
        return {"tag": "", "func": None, "args": {}, "has_at": True}

    def tag_only(self, tag):
        return {"tag": tag.value, "func": None, "args": {}, "has_at": False}

    def tag_with_root(self, tag):
        return {"tag": tag.value, "func": None, "args": {}, "has_at": True}

    def func_only(self, func):
        return {"tag": "", "func": func.value, "args": {}, "has_at": False}

    def func_with_root(self, func):
        return {"tag": "", "func": func.value, "args": {}, "has_at": True}

    def func_with_args(self, func, *argvals):
        args = self._parse_argvals(argvals)
        return {"tag": "", "func": func.value, "args": args, "has_at": False}

    def func_with_args_and_root(self, func, *argvals):
        args = self._parse_argvals(argvals)
        return {"tag": "", "func": func.value, "args": args, "has_at": True}

    def _parse_argvals(self, argvals):
        args = {}
        seen_keys = set()
        for argval in argvals:
            name, val = argval.value.split("|", 1)
            if name in seen_keys:
                raise ValueError(f"Duplicate argument key in tag: '{name}'")
            seen_keys.add(name)
            args[name] = val
        return args





