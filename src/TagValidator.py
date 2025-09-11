#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: September 11, 2025

import re
from typing import Tuple, Dict, Any

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
        'name' : 'adjective',
        'action' : 'creates an adjective with the given attributes'
    },
    'aug': {
        'required': set(),
        'optional': {'f'},
        'name' : 'augmentative',
        'action' : 'handles words with the augmentative suffix "-wasú" or one of its alomorphs',
        'note' : 'superseded by "ev"'
    },
    'card': {
        'required': {'o'},
        'optional': {'s'},
        'name' : 'cardinal',
        'action' : 'creates a cardinal with the given attributes'
    },
    'ev': {
        'required': set(),
        'optional': {'a', 'd', 'f', 'o', 'p', 's', 'x'},
        'name' : 'evaluative',
        'action' : 'handles words with an evaluative suffix, e.g., augmentatives and diminutives'
    },
    'hab': {
        'required': {'x'},
        'optional': {'a', 'f', 'g'},
        'name' : 'habituative',
        'action' : 'handles verb forms with the habituative suffix "-tiwa"'
    },
    'intj': {
        'required': set(),
        'optional': {'o', 's'},
        'name' : 'interjection',
        'action' : 'creates an interjection with the given attributes'
    },
    'mf': {
        'required': {'m'},
        'optional': {'h', 'n', 'o', 'r', 's', 'x'},
        'name' : 'modern form',
        'action' : 'processes historical forms, also parsing their modern equivalents'
    },
    'mid': {
        'required': set(),
        'optional': {'o', 's'},
        'name' : 'middle voice',
        'action' : 'handles verb forms with the "yu-" middle-passive voice prefix'
    },
    'n': {
        'required': {'o'},
        'optional': {'s'},
        'name' : 'noun',
        'action' : 'creates a noun with the given attributes'
    },
    'p': {
        'required': set(),
        'optional': {'o', 's'},
        'name' : 'proper name',
        'action' : 'creates a proper noun with the given attributes'
    },
    'prv': {
        'required': set(),
        'optional': {'x'},
        'name' : 'privative',
        'action' : 'handles words with the privative suffix "-ima"'
    },
    'red': {
        'required': {'l'},
        'optional': {'a', 'o', 'p', 's', 'u', 'x'},
        'name' : 'reduplication',
        'action' : 'handles non-hyphenized reduplication'
    },
    'spl': {
        'required': {'w'},
        'optional': {'b','c', 'h', 'x'},
        'name' : 'split',
        'action' : 'splits two wrongly merged words'
    },
    'typo': {
        'required': {'c'},
        'optional': {'n', 'x'},
        'name' : 'typographical error',
        'action' : 'handles spelling errors not involving wrongly merged words'
    },
    'upos': {
        'required': {'o', 'x'},
        'optional': {'s'},
        'name' : 'universal part of speech',
        'action' : 'creates a word with the specified universal part of speech and other given attributes'
    },
    'v': {
        'required': {'o', 's'},
        'optional': set(),
        'name' : 'verb',
         'action' : 'creates a verb with the given attributes'
    },
    'vnoun': {
        'required': set(),
        'optional': {'a', 'f', 'g', 'p','x'},
        'name' : 'verbal noun',
        'action' : 'handles verb forms with the verbal noun (masdar) suffix "-sawa"'

    },
    'wm': {
        'required': set(),
        'optional': {'x'},
        'name' : 'wrongly merged word',
        'action' : 'assigns the required MISC attributes to the second word obtained by splitting two wrongly merged words'
    }
}
    
# Functions without arguments
ZERO_ARG_FUNCTION_SIGNATURES = { 
    'col': {
        'name': 'collective',
        'action' : 'handles nouns with the collective suffix "-tiwa"'},
    'x': {
        'name': 'other',
        'action' : 'handles non-words — i.e., the right-hand component of a wrongly split word — assigning it the X universal part of speech'
        } 
    }
ZERO_ARG_FUNCTIONS = ['col', 'x']
ZERO_ARG_FUNCTIONS = ZERO_ARG_FUNCTION_SIGNATURES.keys()

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


