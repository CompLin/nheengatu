#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: July 18, 2025
import pytest
from AnnotateConllu import validate_tag
from CompareGoldTestFeats import mkTestSet

def extract_tags():
    import os
    testset=[]
    user=os.path.expanduser('~')
    folder="Dropbox/publications/2025/STIL"
    path=os.path.join(user,folder)
    valid="tags.pdt.txt"
    invalid="tags.pdt.invalid.txt"
    for name in valid, invalid:
        infile=os.path.join(path,name)
        tags=[tag.strip() for tag in open(infile).readlines()]
        testset.append(tags)
    return testset

testset=extract_tags()
treebank_tags=testset[0]
treebank_invalidated_tags=testset[1]

# ---------------------------
# POSITIVE TEST CASES
# ---------------------------
valid_tags = {
    # Functions with required only
    "=a:o|X",
    "=card:o|num",
    "=n:o|thing",
    "=v:o|X:s|Y",
    "=red:l|4",
    "=spl:w|abc",
    "=typo:c|abc",
    "=upos:o|NOUN:x|Pron",
    
    # Functions with required + optional
    "=a:o|X:s|Y",
    "=card:o|num:s|attr",
    "=hab:x|Y:a|t:f|t",
     "=hab:x|Y:a|f:f|f",
    "=mf:m|X:h|Y:n|Z",
    "=red:l|1:a|t:o|q:p|5:s|nom:x|extra",
    "=spl:w|abc:b|t:c|u:h|m:x|n",
    "=typo:c|x:n|q:x|a",
    "=upos:o|X:x|Y:s|Z",

    # Functions with optional only
    "=aug:f|f",
    "=aug:f|t",
    "=ev:p|1:x|extra:o|val:d|f:s|size",
    "=wm:x|thing",
    "=intj:o|oh:s|soft",
    "=mid:o|val:s|type",
    "=p:o|arg:s|style",
    "=prv:x|data",
    "=vnoun:a|f:f|t:g|f:x|info",
    "=vnoun:a|f:f|t:g|t:x|info",

    # Zero-argument functions
    "=col",
    "=x",

    # With @ (root)
    "=red:l|4@",
    "=v:o|run:s|pres@",
    "=card:o|things@",
    "=mf:m|X:h|Y@",
    "=x@",
    "=col@",
}

valid_tags.update(set(treebank_tags))

@pytest.mark.parametrize("tag", valid_tags)
def test_valid_tags(tag):
    """All valid tags should pass validation and return structured output."""
    result = validate_tag(tag)
    assert isinstance(result, dict)


# ---------------------------
# NEGATIVE TEST CASES
# ---------------------------
invalid_tags = {
    # Missing required arguments
    "=a",                     # missing required 'o'
    "=card:s|only",           # missing required 'o'
    "=red:a|t",               # missing required 'l'
    "=typo:x|extra",          # missing required 'c'
    "=v:o|X",                 # missing required 's'
    "=v:s|X",                 # missing required 'o'
    "=upos:o|NOUN",           # missing required 'x'
    "=upos:x|Pron",           # missing required 'o'

    # Invalid argument keys
    "=a:q|bad",               # 'q' is not valid for 'a'
    "=mf:z|oops",             # 'z' is not a valid arg
    "=hab:y|wrong",           # 'y' not in {'x', 'a', 'f', 'g'}
    "=red:l|1:z|oops",        # 'z' not allowed
    "=typo:c|abc:y|xtra",     # 'y' not allowed

    # Too many / duplicate args
    "=a:o|X:o|Y",             # duplicated required arg
    "=ev:p|1:p|2",            # duplicated optional arg
    "=mf:m|1:m|2",            # duplicated required arg
    "=v:o|X:s|Y:s|Z",         # duplicate optional not allowed

    # Extra undefined function
    "=foobar:o|X",            # 'foobar' not defined in FUNCTION_SIGNATURES or ZERO_ARG_FUNCTIONS
    "=hello:x|world",         # undefined function

    # Arguments used in zero-arg function (but allow_empty is True, so they must be excluded)
    "=col:x|bad",             # zero-arg function must not have arguments
    "=x:o|no",                # ditto

    # Invalid uses of root marker or malformed tags
    "@:o|X",                  # '@' cannot take arguments — it's just a root marker
    "=:o|X@",                 # missing function name (should be like =func:...)
    "=@",                    # incomplete: '=' needs a function name, '@' is misplaced
    "=card:o|thing@s",       # '@' is inside the VALUE part, only allowed at the end
    
    # Invalid value for boolean argument
    "=hab:x|Y:a|foo:f|t",
     "=hab:x|Y:a|f:f|foo",
    "=red:l|1:a|true:o|q:p|5:s|nom:x|extra",
    "=aug:f|false",
    "=aug:f|true",
    "=ev:p|1:x|extra:o|val:d|foo:s|size",
    "=vnoun:a|foo:f|hello:g|f:x|info",
    "=vnoun:a|f:f|t:g|true:x|info",
     # Invalid value for integer argument
    "=red:l|4.0",
    "=red:l|m",
    "=red:l|-4",
    "=red:l|1:a|t:o|q:p|0.5:s|nom:x|extra",
     "=red:l|1:a|t:o|q:p|foo:s|nom:x|extra",
     "=red:l|1:a|t:o|q:p|f:s|nom:x|extra",
     "=red:l|1:a|t:o|q:p|t:s|nom:x|extra",

}

invalid_tags.update(set(treebank_invalidated_tags))

@pytest.mark.parametrize("tag", invalid_tags)
def test_invalid_tags(tag):
    """Invalid tags should raise an error."""
    with pytest.raises(Exception):
        validate_tag(tag)
