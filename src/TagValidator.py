#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: June 10, 2025

import re
from typing import Tuple, Dict, Any
from LarkTagValidator import _validate_special_tag as validate_special_tag

# Basic tag pattern: letters, plus sign allowed for compound tags
TAG = r'[a-z]+[0-9]?(\+[a-z]+)*'

# Argument-value pair: both sides can include digits (e.g., arg1|val1)
ARGVAL = r'[a-z][a-z0-9]*\|[\w\-\u00C0-\u024F]+'

# Function name
FUNC = r'[a-z]+'

# 1) @
PAT_ROOT_ONLY = r'^@$'

# 2) tag only
PAT_TAG = fr'^{TAG}$'

# 3) tag with root marker
PAT_TAG_AT = fr'^{TAG}@$'

# 4) function only
PAT_FUNC = fr'^={FUNC}$'

# 5) function with one argval pair
PAT_FUNC_ARG = fr'^={FUNC}:{ARGVAL}$'

# 6) function with multiple argval pairs
PAT_FUNC_ARGS = fr'^={FUNC}(:{ARGVAL})+$'

# 7) function with @
PAT_FUNC_AT = fr'^={FUNC}@$'

# 8) function with argvals and @
PAT_FUNC_ARGS_AT = fr'^={FUNC}(:{ARGVAL})+@$'

# Combine all into one regex list
VALID_PATTERNS = [
    PAT_ROOT_ONLY,
    PAT_TAG,
    PAT_TAG_AT,
    PAT_FUNC,
    PAT_FUNC_ARG,
    PAT_FUNC_ARGS,
    PAT_FUNC_AT,
    PAT_FUNC_ARGS_AT
]

compiled_patterns = [re.compile(p) for p in VALID_PATTERNS]


def _validate_special_tag(tag: str) -> bool:
    """Returns True if tag matches any valid pattern, False otherwise."""
    return any(p.match(tag) for p in compiled_patterns)


def validate_or_raise(tag: str) -> None:
    """Raises ValueError if tag is not valid."""
    if not _validate_special_tag(tag):
        raise ValueError(f"Invalid special tag format: {tag}")

valid = [
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
        "=custom:arg1|val1:arg2|val2:arg3|val3:arg4|val4",
        "=custom:arg1|val1:arg2|val2@",
         "=custom:arg1|val1:arg2|val2:arg3|val3:arg4|val4@",
         "=custom:arg1|val1:arg2|val2:arg3|val3:arg4|val4:arg5|val5",
         "=custom:arg1|val1:arg2|val2:arg3|val3:arg4|val4:arg5|val5:arg6|val6",
         "=custom:arg1|val1:arg2|val2:arg3|val3:arg4|val4:arg5|val5:arg6|val6:arg7|val7",
          "=custom:arg1|val1:arg2|val2:arg3|val3:arg4|val4:arg5|val5@",
         "=custom:arg1|val1:arg2|val2:arg3|val3:arg4|val4:arg5|val5:arg6|val6@",
         "=custom:arg1|val1:arg2|val2:arg3|val3:arg4|val4:arg5|val5:arg6|val6:arg7|val7@",
    ]


invalid = [
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
         "n++",                # trailing ++
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
        "=custom:arg1|val1:arg2|val2:arg3|val3:arg4|val4:arg5|val5:arg6:val6::arg7|val7",
          "=custom:arg1|val1:arg2|val2:arg3|val3:arg4|val4:arg5:val5@",
    ]
    
def test_validate_special_tag():
    print("Testing validate_special_tag:")

    for tag in valid:
        print(f"{tag:<40} => {validate_special_tag(tag)}")  # Expect True
    print("INVALID:")
    for tag in invalid:
        print(f"{tag:<40} => {validate_special_tag(tag)}")  # Expect False
        

ARGUMENTS = {
    'a': 'accent',
    'b': 'base',
    'c': 'correct',
    'd': 'nasal',
    'f': 'force',
    'g': 'guess',
    'h': 'archpos',
    'l': 'length',
    'm': 'modern',
    'n': 'function',
    'o': 'orig',
    'p': 'position',
    'r': 'newregister',
    's': 'orig_form',
    't': 'typo',
    'u': 'suffix',
    'w': 'word',
    'x': 'xpos',
}


BOOLEAN_ARGUMENTS = {'a', 'd', 'f', 'g', 'u'}

INTEGER_ARGUMENTS = {'l','p'}

FUNCTION_SIGNATURES = {
    'a': {
        'required': {'o'},
        'optional': {'s'},
    },
    'aug': {
        'required': set(),
        'optional': {'f'},
    },
    'card': {
        'required': {'o'},
        'optional': {'s'},
    },
    'ev': {
        'required': set(),
        'optional': {'a', 'd', 'f', 'o', 'p', 's', 'x'},
    },
    'hab': {
        'required': {'x'},
        'optional': {'a', 'f', 'g'},
    },
    'hwm': {
        'required': set(),
        'optional': {'x'},
    },
    'intj': {
        'required': set(),
        'optional': {'o', 's'},
    },
    'mf': {
        'required': {'m'},
        'optional': {'h', 'n', 'o', 'r', 's', 'x'},
    },
    'mid': {
        'required': set(),
        'optional': {'o', 's'},
    },
    'n': {
        'required': {'o'},
        'optional': {'s'},
    },
    'p': {
        'required': set(),
        'optional': {'o', 's'},
    },
    'prv': {
        'required': set(),
        'optional': {'x'},
    },
    'red': {
        'required': {'l'},
        'optional': {'a', 'o', 'p', 's', 'u', 'x'},
    },
    'spl': {
        'required': {'w'},
        'optional': {'b','c', 'h', 'x'},
    },
    'typo': {
        'required': {'c'},
        'optional': {'n', 'x'},
    },
    'upos': {
        'required': {'o', 'x'},
        'optional': {'s'},
    },
    'v': {
        'required': {'o', 's'},
        'optional': set(),
    },
    'vnoun': {
        'required': set(),
        'optional': {'a', 'f', 'g', 'x'},
    },
}

    
# Functions without arguments
ZERO_ARG_FUNCTIONS = ['col', 'x']

def include_zero_arg_functions(mapping=FUNCTION_SIGNATURES):
    signature= {'required': set(),'optional': set(),'allow_empty': True}
    for func in ZERO_ARG_FUNCTIONS:
        mapping.update({func : signature})

include_zero_arg_functions()


def validate_function_args(func_name: str, args: Dict[str, str]) -> Tuple[bool, str]:
    """Validate arguments for a function tag based on its signature.

    Assumes that functions with no required arguments can be used without arguments.
    """
    if func_name not in FUNCTION_SIGNATURES:
        return False, f"Function '{func_name}' is not recognized."

    spec = FUNCTION_SIGNATURES[func_name]
    required = spec['required']
    optional = spec.get('optional', set())

    # No arguments provided
    if not args:
        if not required:
            return True, f"Function '{func_name}' correctly used without arguments."
        else:
            return False, f"Function '{func_name}' requires arguments but none were provided."

    # Arguments provided — check required ones
    missing = required - args.keys()
    if missing:
        return False, f"Function '{func_name}' is missing required arguments: {', '.join(missing)}."

    # Check for unknown arguments
    known_args = required | optional
    unknown_args = args.keys() - known_args
    if unknown_args:
        return False, f"Function '{func_name}' has unknown arguments: {', '.join(unknown_args)}."

 # Validate boolean and integer arguments
    for key, val in args.items():
        if key in BOOLEAN_ARGUMENTS and val not in {"t", "f"}:
            raise ValueError(f"Invalid value for boolean argument '{key}': '{val}' (must be 't' or 'f')")
        elif key in INTEGER_ARGUMENTS:
            if not val.isdigit():
                raise ValueError(f"Invalid value for integer argument '{key}': '{val}' (must be an integer)")
    
    return True, f"Function '{func_name}' used correctly with valid arguments."
        
def convert_args(args: Dict[str, str]) -> Dict[str, Any]:
    converted = {}
    for k, v in args.items():
        if k in BOOLEAN_ARGUMENTS:
            converted[k] = (v == "t")
        elif k in INTEGER_ARGUMENTS:
            converted[k] = int(v)
        else:
            converted[k] = v
    return converted

if __name__ == "__main__":
    test_validate_special_tag()

